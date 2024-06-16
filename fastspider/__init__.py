# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2024/6/15 12:24
@Author     : lkkings
@FileName:  : __init__.py.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
from fastspider.http import Request, Response
from fastspider.items import Field, Item
from fastspider.crawler import Crawler,CrawlerTask

__all__ = [
    "__version__",
    "Response",
    "Request",
    "Crawler",
    "CrawlerTask",
    "Item",
    "Field",
]

__author__ = "lkkings"
__version__ = "0.0.1"
__reponame__ = "FastSpider"
__repourl__ = "https://github.com/lkkings/FastSpider.git"

name = __reponame__

CONFIG_FILE_PATH = "conf/conf.yaml"
DEFAULTS_FILE_PATH = "conf/defaults.yaml"
TEST_CONFIG_FILE_PATH = "conf/test.yaml"