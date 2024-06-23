# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2024/6/23 19:45
@Author     : lkkings
@FileName:  : file_utils.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
from pathlib import Path
from typing import Union

import importlib_resources


def ensure_path(path: Union[str, Path]) -> Path:
    """确保路径是一个Path对象 (Ensure the path is a Path object)"""
    return Path(path) if isinstance(path, str) else path

def get_resource_path(filepath: str):
    """获取资源文件的路径 (Get the path of the resource file)

    Args:
        filepath: str: 文件路径 (file path)
    """

    return importlib_resources.files("fastspider") / filepath



def split_filename(text: str, os_limit: dict) -> str:
    """
    根据操作系统的字符限制分割文件名，并用 '......' 代替。

    Args:
        text (str): 要计算的文本
        os_limit (dict): 操作系统的字符限制字典

    Returns:
        str: 分割后的文本
    """
    # 获取操作系统名称和文件名长度限制
    os_name = sys.platform
    filename_length_limit = os_limit.get(os_name, 200)

    # 计算中文字符长度（中文字符长度*3）
    chinese_length = sum(1 for char in text if "\u4e00" <= char <= "\u9fff") * 3
    # 计算英文字符长度
    english_length = sum(1 for char in text if char.isalpha())
    # 计算下划线数量
    num_underscores = text.count("_")

    # 计算总长度
    total_length = chinese_length + english_length + num_underscores

    # 如果总长度超过操作系统限制或手动设置的限制，则根据限制进行分割
    if total_length > filename_length_limit:
        split_index = min(total_length, filename_length_limit) // 2 - 6
        split_text = text[:split_index] + "......" + text[-split_index:]
        return split_text
    else:
        return text