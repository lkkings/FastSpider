# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2024/6/15 23:04
@Author     : lkkings
@FileName:  : __init__.py.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import asyncio
from typing import Dict, Union, List

import aiohttp
from aiohttp import ClientResponse
from aiohttp.client_exceptions import ClientConnectorError
from yarl import URL

from fastspider.exceptions import APIBadRequestError, APIUnauthorizedError, APINotFoundError, APIUnavailableError, \
    APITimeoutError, APIConnectionError, APIError, APIRetryExhaustedError
from fastspider.http.response import Response
from fastspider.logger import logger
from fastspider.utils._trackref import object_ref


class Request(object_ref):
    url: Union[str, URL]
    method: str
    headers: Dict[str, str]
    body: Union[bytes, str]
    cookies: Union[dict, List[dict]]
    encoding: str
    timeout: int

    def __init__(
            self,
            url: str,
            method: str = "GET",
            headers: Dict = None,
            body: Union[bytes, str] = None,
            cookies: Union[dict, List[dict]] = None,
            encoding: str = "utf-8",
            timeout: int = 3,
    ) -> None:
        self.method = str(method).upper()
        self.headers = headers
        self.body = body
        self.timeout = timeout
        self.cookies = cookies
        self._encoding = encoding
        self._url = url

    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def url(self) -> str:
        return self._url

    def raise_for_status(self, response: ClientResponse) -> None:
        if response.status == 200:
            return
        if response.status == 400:
            raise APIBadRequestError(self)
        elif response.status == 403:
            raise APIUnauthorizedError(self)
        elif response.status == 404:
            raise APINotFoundError(self)
        else:
            raise APIUnavailableError(self)

    async def __call__(self, client: aiohttp.ClientSession, retries: int, *args, **kwargs) -> Response:
        try:
            response = await client.request(method=self.method,
                                            url=self.url,
                                            headers=self.headers,
                                            body=self.body,
                                            timeout=self.timeout,
                                            cookies=self.cookies)
            self.raise_for_status(response)
            return Response(response=response)
        except asyncio.TimeoutError:
            raise APITimeoutError(self)
        except ClientConnectorError:
            raise APIConnectionError(self)
        except APIError as e:
            logger.error(e)
            if retries > 0:
                return await self(client, retries - 1, *args, **kwargs)
            raise APIRetryExhaustedError(self)
