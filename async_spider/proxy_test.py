import io, os, sys, time
import typing
sys.path.append("..")
from app.library.tools import get_proxy

from ruia import *


middleware = Middleware()


@middleware.request
async def proxy_middleware(spider_ins, request):

    proxy = get_proxy()
    print(proxy["http"], request.url)
    request.metadata["proxy"] = proxy["http"]

    # https://github.com/howie6879/ruia/issues/128
    # request.aiohttp_kwargs = {"proxy": "http://0.0.0.0:1087"}
    # https://github.com/lixi5338619/asyncpy
    request.aiohttp_kwargs.update({"proxy": proxy["http"]})
    # Just operate request object, and do not return anything.

class ProxySpider(Spider):
    concurrency = 2
    # start_urls = ['https://ip.gs/json' for x in range(5)]
    start_urls = ['https://api.ip.sb/ip' for x in range(5)]

    async def parse(self, response):
        res = await response.json()
        print(f'proxy: {response.metadata["proxy"]}, res: {res}')

if __name__ == "__main__":
    ProxySpider.start(middleware=middleware)