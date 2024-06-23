# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2024/6/23 19:50
@Author     : lkkings
@FileName:  : http_utils.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import re
from typing import Union, List
from urllib.parse import urlparse


def split_set_cookie(cookie_str: str) -> str:
    """
    拆分Set-Cookie字符串并拼接 (Split the Set-Cookie string and concatenate)

    Args:
        cookie_str (str): 待拆分的Set-Cookie字符串 (The Set-Cookie string to be split)

    Returns:
        str: 拼接后的Cookie字符串 (Concatenated cookie string)
    """

    # 判断是否为字符串 / Check if it's a string
    if not isinstance(cookie_str, str):
        raise TypeError("`set-cookie` must be str")

    # 拆分Set-Cookie字符串,避免错误地在expires字段的值中分割字符串 (Split the Set-Cookie string, avoiding incorrect splitting on the value of the 'expires' field)
    # 拆分每个Cookie字符串，只获取第一个分段（即key=value部分） / Split each Cookie string, only getting the first segment (i.e., key=value part)
    # 拼接所有的Cookie (Concatenate all cookies)
    return ";".join(
        cookie.split(";")[0] for cookie in re.split(", (?=[a-zA-Z])", cookie_str)
    )


def split_dict_cookie(cookie_dict: dict) -> str:
    return "; ".join(f"{key}={value}" for key, value in cookie_dict.items())


def extract_valid_urls(inputs: Union[str, List[str]]) -> Union[str, List[str], None]:
    """从输入中提取有效的URL (Extract valid URLs from input)

    Args:
        inputs (Union[str, list[str]]): 输入的字符串或字符串列表 (Input string or list of strings)

    Returns:
        Union[str, list[str]]: 提取出的有效URL或URL列表 (Extracted valid URL or list of URLs)
    """
    url_pattern = re.compile(r"https?://\S+")

    # 如果输入是单个字符串
    if isinstance(inputs, str):
        match = url_pattern.search(inputs)
        return match.group(0) if match else None

    # 如果输入是字符串列表
    elif isinstance(inputs, list):
        valid_urls = []

        for input_str in inputs:
            matches = url_pattern.findall(input_str)
            if matches:
                valid_urls.extend(matches)

        return valid_urls


def get_host_and_port_from_ws(ws_url):
    parsed_url = urlparse(ws_url)
    if parsed_url.scheme == "ws":
        host = parsed_url.hostname
        port = parsed_url.port if parsed_url.port else 80  # 默认端口号为 80
        return host, port
    else:
        raise ValueError("Invalid WebSocket URL")