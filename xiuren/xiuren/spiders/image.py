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
            # xiuren album
            # albums = session.query(XiurenAlbum).filter(XiurenAlbum.cover_backup == None).all()
            # for album in albums:
            #     self.datas.append({"id": album.id, "cover": album.cover})
                # break
            # xiuren image
            images = session.query(XiurenImage).filter(XiurenImage.backup_url == None).limit(1).all()
            print(f"start id: {images[0].id}, end id: {images[-1].id}, total count: {len(images)}")
            for image in images:
                self.datas.append({"id": image.id, "image_url": image.image_url.replace("www.xiurenb.cc","p.xiurenb.cc")})

    def start_requests(self):
        for data in self.datas:
            yield scrapy.Request(url=data["image_url"], callback=self.parse, meta={"id": data["id"], "image_url": data["image_url"]})

    def parse(self, response):

        if response.status == 200:
            item = XiurenImageItem()
            item["ct"] = "image"
            item["content"] = response.body
            item["id"] = response.meta["id"]
            image_url = response.meta["image_url"]

            item["ext"] = image_url.split(".")[-1]
            item["b2_key"] = re.split('/', image_url.replace("https://", "").replace("http://", ""), maxsplit=1)[-1]
            yield item