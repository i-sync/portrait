import io, os, sys, time
import typing
sys.path.append("..")
from app.library.tools import get_proxy

import asyncio
import aiohttp
from ruia import *

from aiosocksy.connector import ProxyConnector, ProxyClientRequest

# https://github.com/aio-libs/aiohttp/discussions/6044
# setattr(asyncio.sslproto._SSLProtocolTransport, "_start_tls_compatible", True)

middleware = Middleware()


@middleware.request
async def proxy_middleware(spider_ins, request):

    proxy = get_proxy()
    print(proxy["https"], request.url)
    request.metadata["proxy"] = proxy["https"]

    # https://github.com/howie6879/ruia/issues/128
    request.aiohttp_kwargs = {"proxy":  proxy["https"] } # "http://127.0.0.1:8123" }
    # request.aiohttp_kwargs = {"proxy": "socks5://127.0.0.1:1080" }

    # https://github.com/lixi5338619/asyncpy
    # request.aiohttp_kwargs.update({"proxy": proxy["https"]})
    # Just operate request object, and do not return anything.

class ProxySpider(Spider):
    concurrency = 2
    # start_urls = ['https://ip.gs/json' for x in range(5)]
    start_urls = ['https://api-ipv4.ip.sb/ip' for x in range(5)]
    # start_urls = ['https://viagle.cn' for x in range(5)]


    async def process_start_urls(self):
        for url in self.start_urls:
            request_session = aiohttp.ClientSession(connector=ProxyConnector(), request_class=ProxyClientRequest)
            # yield self.request(url=image_url, callback=self.parse, metadata={"image_id": image.id, "image_url": image_url}, request_session=request_session)
            yield self.request(url=url, callback=self.parse, request_session=request_session)

    async def parse(self, response):
        res = await response.text()
        # print(res)
        print(f'proxy: {response.metadata["proxy"]}, res: {res}')

if __name__ == "__main__":
    ProxySpider.start(middleware=middleware)
    # ProxySpider.start()