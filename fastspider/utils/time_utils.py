# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2024/6/23 19:47
@Author     : lkkings
@FileName:  : time_utils.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import datetime
from datetime import datetime
from typing import Union


def get_timestamp(unit: str = "milli"):
    """
    根据给定的单位获取当前时间 (Get the current time based on the given unit)

    Args:
        unit (str): 时间单位，可以是 "milli"、"sec"、"min" 等
            (The time unit, which can be "milli", "sec", "min", etc.)

    Returns:
        int: 根据给定单位的当前时间 (The current time based on the given unit)
    """

    now = datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
    if unit == "milli":
        return int(now.total_seconds() * 1000)
    elif unit == "sec":
        return int(now.total_seconds())
    elif unit == "min":
        return int(now.total_seconds() / 60)
    else:
        raise ValueError("Unsupported time unit")


def timestamp_2_str(
        timestamp: Union[str, int, float], format: str = "%Y-%m-%d %H-%M-%S"
) -> Union[str, datetime]:
    """
    将 UNIX 时间戳转换为格式化字符串 (Convert a UNIX timestamp to a formatted string)

    Args:
        timestamp (int): 要转换的 UNIX 时间戳 (The UNIX timestamp to be converted)
        format (str, optional): 返回的日期时间字符串的格式。
                                默认为 '%Y-%m-%d %H-%M-%S'。
                                (The format for the returned date-time string
                                Defaults to '%Y-%m-%d %H-%M-%S')

    Returns:
        str: 格式化的日期时间字符串 (The formatted date-time string)
    """
    if timestamp is None or timestamp == "None":
        return ""

    if isinstance(timestamp, str):
        if len(timestamp) == 30:
            return datetime.datetime.strptime(timestamp, "%a %b %d %H:%M:%S %z %Y")

    return datetime.datetime.fromtimestamp(float(timestamp)).strftime(format)

