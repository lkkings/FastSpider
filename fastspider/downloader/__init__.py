# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2024/6/15 16:22
@Author     : lkkings
@FileName:  : __init__.py.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import asyncio
import os
from asyncio import BaseEventLoop, AbstractEventLoop
from pathlib import Path
from typing import Union, Any, Dict, Tuple
from urllib.parse import unquote

import aiofiles
import aiohttp
from rich.progress import TaskID

from fastspider.logger import logger
from fastspider.utils._signal import SignalManager
from fastspider.utils.console_manager import RichConsoleManager
from fastspider.utils.file_utils import ensure_path
from fastspider.utils.pause_resume import AsyncPauseAbleTask
from fastspider.http import Request, Response


def get_chunk_size(file_size: int) -> int:
    """
    根据文件大小确定合适的下载块大小 (Determine appropriate download chunk size based on file size)

    Args:
        file_size (int): 文件大小，单位为字节 (File size in bytes)

    Returns:
        int: 下载块的大小 (Size of the download chunk)
    """

    # 文件大小单位为字节 (File size is in bytes)
    if file_size < 10 * 1024:  # 小于10KB (Less than 10KB)
        return file_size  # 一次性下载整个文件 (Download the entire file at once)
    elif file_size < 1 * 1024 * 1024:  # 小于1MB (Less than 1MB)
        return file_size // 10
    elif file_size < 10 * 1024 * 1024:  # 小于10MB (Less than 10MB)
        return file_size // 20
    elif file_size < 100 * 1024 * 1024:  # 小于100MB (Less than 100MB)
        return file_size // 50
    else:  # 文件大小大于100MB (File size greater than 100MB)
        return 1 * 1024 * 1024  # 使用1MB的块大小 (Use a chunk size of 1MB)


async def _get_file_info(request: Request):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url=request.url, headers=request.headers, cookies=request.cookies) as response:
                # 获取 Content-Disposition 头信息
                content_disposition = response.headers.get('Content-Disposition')
                content_length = int(response.headers.get('Content-Length', 0))
                if content_disposition:
                    # 从 Content-Disposition 头信息中解析出文件名
                    filename = content_disposition.split('filename=')[-1]
                    filename = filename.strip('";\' ')
                else:
                    # 如果没有 Content-Disposition 头信息，则从 URL 中提取文件名
                    filename = os.path.basename(request.url)
                # 解码文件名（如果有必要）
                filename = unquote(filename)
                # 获取文件后缀名
                filename, file_extension = os.path.splitext(filename)
                return filename, file_extension, content_length

    except aiohttp.ClientError as e:
        logger.error(e)
        return None, None, 0


def trim_filename(filename: Union[str, Path], max_length: int = 50) -> str:
    """
    裁剪文件名以适应控制台显示 (Trim the filename to fit console display)

    Args:
        filename (str or Path): 完整的文件名 (Full filename)
        max_length (int): 显示的最大字符数 (Maximum number of characters to display)

    Returns:
        裁剪后的文件名 (trimmed filename)
    """

    filename = str(ensure_path(filename))

    prefix_suffix_len = max_length // 2 - 2

    # 如果文件名长度超过最大长度，则进行裁剪
    return (
        f"{filename[:prefix_suffix_len]}...{filename[-prefix_suffix_len:]}"
        if len(str(filename)) > max_length
        else filename
    )


class Downloader(AsyncPauseAbleTask):
    def __init__(self,cfg: Dict, loop: AbstractEventLoop = None):
        cfg = cfg.get('downloader', {}).copy()
        super().__init__(cfg, loop)
        self._download_tasks = {}
        self._no_download_flag = []
        self._save_path = cfg['save_path']
        self._progress = RichConsoleManager().progress

    @staticmethod
    def _ensure_path(path: Union[str, Path]) -> Path:
        return ensure_path(path)

    async def put_task(self, task: Tuple[Request, str]):
        request, filename = task
        if request.url in self._no_download_flag:
            self._no_download_flag.remove(request.url)
        await self._task_queue.put((request, filename))

    def remove_task(self, request: Request):
        url = request.url
        if url in self._download_tasks:
            task = self._download_tasks[url]
            task.cancel()
            del self._download_tasks[request.url]
        else:
            self._no_download_flag.append(url)

    async def _download_chunks(self, request: Request, content_length: int, file: Any, task_id: TaskID):
        try:
            response: Response = await request(self._client, self._cfg['retries'])
            chunk_size = get_chunk_size(content_length)
            async for chunk in response.content.iter_chunked(chunk_size):
                if SignalManager.is_shutdown_signaled():
                    break
                await file.write(chunk)
                await self._progress.update(
                    task_id, advance=len(chunk), total=int(content_length)
                )
        except asyncio.TimeoutError as e:
            logger.warning(f"文件区块下载超时：{e}")
        except Exception as e:
            logger.error(f"文件区块下载失败：{e}")

    async def _download(self, request: Request, filename: str):
        _filename, file_extension, content_length = await _get_file_info(request)
        if not filename:
            filename = _filename
        if content_length == 0:
            logger.warning(
                "链接 {0} 内容长度为0，尝试下一个链接是否可用".format(request.url)
            )
            return
        logger.debug(
            "{0} 在服务器上的总内容长度为：{1} 字节".format(
                request.url, content_length
            )
        )
        full_path = Path(str(os.path.join(self._save_path, filename)))
        filename = trim_filename(full_path.name, 45)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = full_path.with_suffix(".tmp")
        start_byte = 0
        if os.path.exists(tmp_path):
            tmp_file_size = tmp_path.stat().st_size
            if tmp_file_size < content_length:
                logger.debug(
                    "找到了未下载完的文件 {0}, 大小为 {1} 字节".format(
                        tmp_path, start_byte
                    )
                )
                task_id = await self._progress.add_task(
                    description="[  {0}  ]:".format(file_extension),
                    filename=filename,
                    start=True,
                )
                await self._progress.update(task_id, state="starting")
                await self._progress.update(
                    task_id, advance=tmp_file_size, total=int(content_length)
                )
                start_byte = tmp_file_size
            else:
                logger.debug("临时文件{}已完全下载".format(tmp_path))
                task_id = await self._progress.add_task(
                    description="[  跳过  ]:",
                    filename=filename,
                    start=True,
                    total=1,
                    completed=1,
                )
                await self._progress.update(task_id, state="completed")
                return
        request.headers['Range'] = f'bytes={start_byte}-'
        async with aiofiles.open(
                tmp_path, "ab" if start_byte else "wb"
        ) as file:
            await self._download_chunks(
                request, content_length, file, task_id
            )
        # 下载完成后重命名文件 (Rename file after download is complete)
        try:
            tmp_path.rename(full_path)
        except FileExistsError:
            logger.warning("{0} 已存在，将覆盖").format(full_path)
            tmp_path.replace(full_path)
        except PermissionError:
            logger.error(
                "另一个程序正在使用此文件或受异步调度影响，该任务需要重新下载"
            )
            # 尝试删除临时文件 (Try to delete the temporary file)
            try:
                tmp_path.unlink()
                tmp_path.rename(full_path)
            except Exception as e:
                logger.error("尝试删除临时文件失败：{0}".format(e))
            await self._progress.update(
                task_id,
                description="[  失败  ]：",
                filename=filename,
                state="error",
            )

        await self._progress.update(
            task_id,
            description="[  完成  ]：",
            filename=filename,
            state="completed",
        )
        logger.debug("下载完成, 文件已保存为 {0}".format(full_path))
        self._semaphore.release()
        del self._download_tasks[request.url]

    async def _task_handler(self, task_queue: asyncio.Queue):
        request, filename = await task_queue.get()
        if request.url in self._no_download_flag:
            return
        task = self._loop.create_task(self._download(request, filename))
        self._download_tasks[request.url] = task
