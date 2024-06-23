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

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
import aiohttp
from aiohttp import ClientResponse
from aiohttp.client_exceptions import ClientConnectorError

from fastspider.exceptions import APIBadRequestError, APIUnauthorizedError, APINotFoundError, APIUnavailableError, \
    APITimeoutError, APIConnectionError, APIError, APIRetryExhaustedError
from fastspider.http.response import Response
from fastspider.logger import logger
from fastspider.utils._trackref import object_ref


class Request(object_ref):
    excluded_error_codes = []

    def __init__(
            self,
            url: str,
            method: str = "GET",
            headers=None,
            cookies=None,
            proxy=None,
            encoding: str = 'utf-8',

            **kwargs: Any
    ) -> None:
        if headers is None:
            headers = {}
        self.method = str(method).upper()
        self.proxy = proxy
        self.headers = headers
        self.cookies = cookies
        self.kwargs = kwargs
        self._encoding = encoding
        self._url = url



    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def url(self) -> str:
        return self._url

    def raise_for_status(self, response: ClientResponse) -> None:
        if response.status == 200 or response.status in self.excluded_error_codes:
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
                                            proxy=self.proxy,
                                            cookies=self.cookies,
                                            **self.kwargs)
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
