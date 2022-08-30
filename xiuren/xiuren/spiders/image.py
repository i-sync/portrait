import re, os, sys, time, random
sys.path.append("..")
import scrapy
from bs4 import BeautifulSoup
from app.library.models import session_scope, XiurenAlbum, XiurenImage
from xiuren.items import XiurenImageItem

class ImageSpider(scrapy.Spider):
    name = 'image'

    start_urls = ['http://baidu.com/']

    datas = []
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            #'xiuren.middlewares.XiurenAlbumMiddleware': 500,
            'xiuren.middlewares.XiurenProxyMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'xiuren.pipelines.XiurenImagePipeline': 300,
        }
    }


    def __init__(self):
        super().__init__()
        with session_scope() as session:
            albums = session.query(XiurenAlbum).filter(XiurenAlbum.cover_backup == None).all()
            for album in albums:
                self.datas.append({"id": album.id, "cover": album.cover})
                # break

    def start_requests(self):
        for data in self.datas:
            yield scrapy.Request(url=data["cover"], callback=self.parse, meta={"id": data["id"], "cover": data["cover"]})

    def parse(self, response):

        if response.status == 200:
            item = XiurenImageItem()
            item["ct"] = "album"
            item["content"] = response.body
            item["id"] = response.meta["id"]
            cover = response.meta["cover"]

            item["ext"] = cover.split(".")[-1]
            item["b2_key"] = re.split('/', cover.replace("https://", "").replace("http://", ""), maxsplit=1)[-1]
            yield item