import io, os, sys, time
import typing
sys.path.append("..")
from app.library.tools import get_proxy

import asyncio
from ruia import *

# https://github.com/aio-libs/aiohttp/discussions/6044
setattr(asyncio.sslproto._SSLProtocolTransport, "_start_tls_compatible", True)

middleware = Middleware()


@middleware.request
async def proxy_middleware(spider_ins, request):

    proxy = get_proxy()
    print(proxy["https"], request.url)
    request.metadata["proxy"] = proxy["https"]

    # https://github.com/howie6879/ruia/issues/128
    # request.aiohttp_kwargs = {"proxy": "http://0.0.0.0:1087"}
    # https://github.com/lixi5338619/asyncpy
    request.aiohttp_kwargs.update({"proxy": proxy["https"]})
    # Just operate request object, and do not return anything.

class ProxySpider(Spider):
    concurrency = 2
    # start_urls = ['https://ip.gs/json' for x in range(5)]
    start_urls = ['https://api.ip.sb/ip' for x in range(5)]

    async def parse(self, response):
        res = await response.text()
        print(f'proxy: {response.metadata["proxy"]}, res: {res}')

if __name__ == "__main__":
    ProxySpider.start(middleware=middleware)