import re, os, sys, time, random
sys.path.append("..")
import scrapy
from bs4 import BeautifulSoup
from app.library.config import configs
from app.library.models import session_scope, XiurenAlbum, XiurenImage
from xiuren.items import XiurenImageItem

IMAGE_PATH = "/mnt/portrait"

class ImageSpider(scrapy.Spider):
    name = 'image'

    start_urls = ['http://baidu.com/']

    datas = []
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            #'xiuren.middlewares.XiurenAlbumMiddleware': 500,
            #'xiuren.middlewares.XiurenProxyMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'xiuren.pipelines.XiurenImagePipeline': 300,
        }
    }


    def insert_slash_between_year_month(self, input_string):
        # 定义匹配年月的正则表达式
        pattern = r'/(\d{4})(\d{2})/'

        # 使用正则表达式进行匹配和替换
        modified_string = re.sub(pattern, r'/\1/\2/', input_string)

        return modified_string

    def __init__(self):
        super().__init__()
        with session_scope() as session:
            # xiuren album
            # albums = session.query(XiurenAlbum).filter(XiurenAlbum.cover_backup == None).all()
            # for album in albums:
            #     self.datas.append({"id": album.id, "cover": album.cover})
                # break
            # xiuren image
            #images = session.query(XiurenImage).filter().limit(1).all()
            #print(f"start id: {images[0].id}, end id: {images[-1].id}, total count: {len(images)}")
            #for image in images:
            #    self.datas.append({"id": image.id, "image_url": image.image_url.replace("www.xiurenb.cc","p.xiurenb.cc")})

            images = session.query(XiurenImage).filter(XiurenImage.backup_url.op('regexp')('uploadfile/[0-9]{6}/')).limit(10000).all()
            for image in images:
                image_path = re.split('/', image.image_url.replace("https://", "").replace("http://", ""), maxsplit=1)[-1]
                #print(image_path)
                new_image_path = self.insert_slash_between_year_month(image_path)
                local_path = f'{IMAGE_PATH}/{new_image_path}'
                if os.path.exists(local_path):
                    print(local_path, "exists, skip...")
                    continue
                image_url = image.image_url.replace("www.xiurenb.vip","0814a.3tp.club").replace("www.xiurenb.net","0814a.3tp.club").replace("www.xiurenb.com","0814a.3tp.club")
                #image_url = f'{configs.meta.image_url}{image_path}'
                self.datas.append({"id": image.id, "image_url": image_url, "new_image_path": new_image_path})
                # yield self.request(url=image_url, callback=self.parse, metadata={"image_id": image.id, "image_url": image_url, "new_image_path": new_image_path})

    def start_requests(self):
        for data in self.datas:
            yield scrapy.Request(url=data["image_url"], callback=self.parse, meta={"id": data["id"], "image_url": data["image_url"], "new_image_path": data["new_image_path"]})

    def parse(self, response):

        if response.status == 200:
            item = XiurenImageItem()
            item["ct"] = "image"
            item["content"] = response.body
            item["id"] = response.meta["id"]
            item["new_image_path"] = response.meta["new_image_path"]

            # item["ext"] = image_url.split(".")[-1]
            # item["b2_key"] = re.split('/', image_url.replace("https://", "").replace("http://", ""), maxsplit=1)[-1]
            yield item