import io, os, re, sys, time
import typing
sys.path.append("..")
from app.library.config import configs
from app.library.tools import get_proxy
from app.library.models import session_scope, XiurenAlbum, XiurenImage, XiurenCategory, XiurenTag

from app.library.b2s3 import get_b2_client, get_b2_resource, key_exists

import aiofiles
from ruia import *


import asyncio

# https://github.com/aio-libs/aiohttp/discussions/6044
setattr(asyncio.sslproto._SSLProtocolTransport, "_start_tls_compatible", True)

middleware = Middleware()

@middleware.request
async def proxy_middleware(spider_ins, request):

    proxy = get_proxy()
    print(proxy["https"], request.url)

    # https://github.com/howie6879/ruia/issues/128
    # request.aiohttp_kwargs = {"proxy": "http://0.0.0.0:1087"}
    # https://github.com/lixi5338619/asyncpy
    request.aiohttp_kwargs.update({"proxy": proxy["https"]})
    # Just operate request object, and do not return anything.

class ImageSpider(Spider):
    concurrency = 20
    start_urls = ['https://www.github.com']

    async def process_start_urls(self):

        with session_scope() as session:
            # xiuren image
            images = session.query(XiurenImage).filter(XiurenImage.backup_url == None).limit(5).all()
            print(f"start id: {images[0].id}, end id: {images[-1].id}, total count: {len(images)}")
            for image in images:
                image_url = image.image_url.replace("www.xiurenb.com","p.xiurenb.cc").replace("www.xiurenb.net","p.xiurenb.cc")
                yield self.request(url=image_url, callback=self.parse, metadata={"image_id": image.id, "image_url": image_url})


    async def parse(self, response):
        print(response.status)
        if response.status == -1:
            image_id = response.metadata["image_id"]
            image_url = response.metadata["image_url"]
            with session_scope() as session:
                image = session.query(XiurenImage).filter(XiurenImage.id == image_id).first()
                if image:
                    image.backup_url = "error"
                else:
                    print(f"image not found, image_id:{image_id}")
                session.commit()
                print(f"image download error!: id: {image_id},  url: {image_url}")

        elif response.status < 400:
            image_id = response.metadata["image_id"]
            image_url = response.metadata["image_url"]

            ext = image_url.split(".")[-1]
            b2_key = re.split('/', image_url.replace("https://", "").replace("http://", ""), maxsplit=1)[-1]

            print(f"{image_id}, {b2_key}, start time: {time.time()}")

            try:
                content = await response.read()
            except Exception as e:
                print(e)
            else:
                # boto3, upload to b2

                # b2 = get_b2_resource()
                b2_client = get_b2_client()
                bucket_name = configs.b2.bucket_name

                # b2.Object(bucket_name, b2_key).put(Body=buf, ContentType=f"image/{ext}")
                b2_client.put_object(Body=content, Bucket=bucket_name, Key=b2_key, ContentType=f"image/{ext}")
                print(f"image upload b2 finish, b2_key:{b2_key}")

                with session_scope() as session:
                    image = session.query(XiurenImage).filter(XiurenImage.id == image_id).first()
                    if image:
                        image.backup_url = b2_key
                    else:
                        print(f"image not found, image_id:{image_id}")
                    session.commit()

            print(f"{image_id}, {b2_key}, end time: {time.time()}")


if __name__ == "__main__":
    ImageSpider.start(middleware=middleware)