import io, os, re, sys, time
import typing
sys.path.append("..")
from app.library.config import configs
from app.library.tools import get_proxy
from app.library.models import session_scope, XiurenAlbum, XiurenImage, XiurenCategory, XiurenTag

from app.library.b2s3 import get_b2_client, get_b2_resource, key_exists

import aiofiles
from ruia import *
from ruia_ua import middleware


import asyncio

IMAGE_PATH = "/mnt/portrait"

# https://github.com/aio-libs/aiohttp/discussions/6044
setattr(asyncio.sslproto._SSLProtocolTransport, "_start_tls_compatible", True)

#middleware = Middleware()

#@middleware.request
#async def proxy_middleware(spider_ins, request):

#    proxy = get_proxy()
#    print(proxy["https"], request.url)

    # https://github.com/howie6879/ruia/issues/128
    # request.aiohttp_kwargs = {"proxy": "http://0.0.0.0:1087"}
    # https://github.com/lixi5338619/asyncpy
    # request.aiohttp_kwargs.update({"proxy": proxy["https"]})
    # Just operate request object, and do not return anything.


def insert_slash_between_year_month(input_string):
    # 定义匹配年月的正则表达式
    pattern = r'/(\d{4})(\d{2})/'

    # 使用正则表达式进行匹配和替换
    modified_string = re.sub(pattern, r'/\1/\2/', input_string)

    return modified_string

class ImageSpider(Spider):
    concurrency = 30
    start_urls = ['https://www.github.com']

    async def process_start_urls(self):

        with session_scope() as session:
            # xiuren image
            images = session.query(XiurenImage).filter().offset(300).limit(100).all()
            #print(f"start id: {images[0].id}, end id: {images[-1].id}, total count: {len(images)}")
            for image in images:
                image_path = re.split('/', image.image_url.replace("https://", "").replace("http://", ""), maxsplit=1)[-1]
                new_image_path = insert_slash_between_year_month(image_path)
                local_path = f'{IMAGE_PATH}/{new_image_path}'
                if os.path.exists(local_path):
                    print(local_path, "exists, skip...")
                    continue
                #image_url = image.image_url.replace("www.xiurenb.vip","x0811a.20dh.top").replace("www.xiurenb.net","x0811a.20dh.top").replace("www.xiurenb.com","x0811a.20dh.top")
                image_url = f'{configs.meta.image_url}{image.backup_url}'
                yield self.request(url=image_url, callback=self.parse, metadata={"image_id": image.id, "image_url": image_url, "new_image_path": new_image_path})


    async def parse(self, response):
        print(response.status)
        if response.status == -1:
            # image_id = response.metadata["image_id"]
            # image_url = response.metadata["image_url"]
            # with session_scope() as session:
            #     image = session.query(XiurenImage).filter(XiurenImage.id == image_id).first()
            #     if image:
            #         image.backup_url = "error"
            #     else:
            #         print(f"image not found, image_id:{image_id}")
            #     session.commit()
            print(f"image download error!: id: {image_id},  url: {image_url}")

        elif response.status < 400:
            image_id = response.metadata["image_id"]
            image_url = response.metadata["image_url"]
            new_image_path = response.metadata["new_image_path"]

            local_path = f'{IMAGE_PATH}/{new_image_path}'

            # check folder exists , if not ,create.
            local_dir = os.path.dirname(local_path)
            os.makedirs(local_dir, exist_ok=True)

            try:
                content = await response.read()
            except Exception as e:
                print(e)
            else:

                with open(f'{IMAGE_PATH}/{new_image_path}', 'wb') as f:
                    f.write(content)

                with session_scope() as session:
                    image = session.query(XiurenImage).filter(XiurenImage.id == image_id).first()
                    if image:
                        image.backup_url = new_image_path
                    else:
                        print(f"image not found, image_id:{image_id}")
                    session.commit()

            print(f"{image_id}, {new_image_path}, end time: {time.time()}")


if __name__ == "__main__":
    ImageSpider.start(middleware=middleware)