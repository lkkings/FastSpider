# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2024/6/16 1:12
@Author     : lkkings
@FileName:  : response.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
from http.cookies import SimpleCookie
from typing import Dict, Union, List, Tuple

from aiohttp import ClientResponse
from yarl import URL

from fastspider.utils._trackref import object_ref


class Response(object_ref):
    _response: ClientResponse = None
    from_todo: Union[str, Tuple]

    def __init__(self, response: ClientResponse, **kwargs):
        self._response = response

    @property
    def r(self):
        return self._response

    @property
    def url(self) -> URL:
        return self._response.url

    @property
    def status(self) -> int:
        return self._response.status

    @property
    def content(self):
        return self._response.content

    def cookies(self) -> SimpleCookie[str]:
        return self._response.cookies

    def __repr__(self):
        return f"<{self._response.status} {self.url}>"

    async def text(self):
        return await self._response.text()

    def close(self):
        self._response.close()

    async def json(self):
        return await self._response.json()

    def css(self, *a, **kw):
        """Shortcut method implemented only by responses whose content
        is text (subclasses of TextResponse).
        """
        raise NotSupportedError("Response content isn't text")

    def jmespath(self, *a, **kw):
        """Shortcut method implemented only by responses whose content
        is text (subclasses of TextResponse).
        """
        raise NotSupportedError("Response content isn't text")

    def xpath(self, *a, **kw):
        """Shortcut method implemented only by responses whose content
        is text (subclasses of TextResponse).
        """
        raise NotSupportedError("Response content isn't text")
