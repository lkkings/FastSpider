import aiohttp
import httpx


class HTTPClient:
    session = None

    async def request(self, method, url, **kwargs):
        return await self.session.request(method, url, **kwargs)


class AiohttpClient(HTTPClient):

    def __init__(self, **kwargs):
        self.session = aiohttp.ClientSession(**kwargs)


class HttpxClient(HTTPClient):

    def __init__(self, **kwargs):
        self.session = httpx.AsyncClient(**kwargs)


class HTTPClientFactory:
    @staticmethod
    def get_client(client_type="aiohttp", **kwargs) -> HTTPClient:
        if client_type == "aiohttp":
            return AiohttpClient(**kwargs)
        elif client_type == "httpx":
            return HttpxClient(**kwargs)
        else:
            raise ValueError(f"Unknown client type: {client_type}")
