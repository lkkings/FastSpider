from pathlib import Path
from typing import Union


class Error(Exception):
    code: int = None
    description: str = None


class APIError(Error):
    def __init__(self, request, message: str = None):
        super().__init__(f'[{self.code}] Desc: {self.description}  API: {request.url}  Message: {message}')


class APIConnectionError(APIError):
    """当与API的连接出现问题时抛出"""
    code = 100001
    description = 'API连接异常，请检查网络设置！'


class APIUnavailableError(APIError):
    """当API服务不可用时抛出，例如维护或超时"""
    code = 100002
    description = 'API服务不可用'


class APINotFoundError(APIError):
    code = 100003
    description = 'API端点不存在'


class APIResponseError(APIError):
    """当API返回的响应与预期不符时抛出"""
    code = 100004
    description = 'API返回的响应与预期不符'


class APIRateLimitError(APIError):
    """当达到API的请求速率限制时抛出"""
    code = 100005
    description = '达到API的请求速率限制'


class APITimeoutError(APIError):
    """当API请求超时时抛出"""
    code = 100006
    description = 'API请求超时'


class APIUnauthorizedError(APIError):
    """当API请求由于授权失败而被拒绝时抛出"""
    code = 100007
    description = '权限不足'


class APIRetryExhaustedError(APIError):
    """当API请求重试次数用尽时抛出"""
    code = 100008
    description = 'API请求重试次数用尽'


class APIBadRequestError(APIError):
    """当API请求重试次数用尽时抛出"""
    code = 100009
    description = 'API客户端发送错误请求'


class FileError(Error):
    def __init__(self, file_path: Union[Path, str], message: str = None):
        super().__init__(f'[{self.code}] Desc: {self.description}  FilePath: {file_path}  Message: {message}')


class FileNotFound(Error):
    """文件不存在错误"""
    code = 200001
    description = '文件不存在'


class FilePermissionError(FileError):
    """文件权限错误"""
    code = 200002
    description = '文件权限错误'


class FileReadError(FileError):
    """文件读取错误"""
    code = 200003
    description = '文件读取错误'


class FileWriteError(FileError):
    """文件写入错误"""
    code = 200004
    description = '文件写入错误'


class ObjectError(Error):
    def __init__(self, o: object, message: str = None):
        super().__init__(f'[{self.code}] Desc: {self.description}  Object: {o.__name__}  Message: {message}')


class NotAsyncMethodError(ObjectError):
    code = 300001
    description = '对象不是一个异步方法'


class MethodReturnError(ObjectError):
    code = 300002
    description = '对象返回类型错误'


class ClassTypeError(ObjectError):
    code = 300003
    description = '对象类型错误'
