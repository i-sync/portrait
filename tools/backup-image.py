# coding=UTF-8
import io
import re
import os
import sys
import time

import requests

from sqlalchemy import func, desc

sys.path.append('../')
from app.library.config import configs
from app.library.page import Page
from app.library.models import session_scope, XiurenAlbum, XiurenImage, XiurenCategory

from app.library.b2s3 import get_b2_resource, key_exists


def get_image_content(image_url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    }
    res = requests.get(image_url, headers=headers)
    if res.status_code != 200:
        return None
    return io.BytesIO(res.content)


def image_backup_album():

    b2 = get_b2_resource()

    bucket_name = configs.b2.bucket_name

    with session_scope() as session:
        albums = session.query(XiurenAlbum).filter(XiurenAlbum.cover_backup == None).limit(10).all()

        for album in albums:
            cover = album.cover
            #print(cover)
            ext = cover.split(".")[-1]
            b2_file_path = re.split('/', cover.replace("https://", "").replace("http://", ""), maxsplit=1)[-1]
            print(b2_file_path)
            # check b2 file if exists
            if not key_exists(b2, bucket_name, b2_file_path):
                # not exist , download file and upload
                buf = get_image_content(cover)
                if buf:
                    b2.Object(bucket_name, b2_file_path).put(Body=buf, ContentType=f"image/{ext}")
                else:
                    print(f"image download failed, {cover}")
            else:
                #exists , skip upload,
                print(b2_file_path, "exists on b2, skip...")
            album.cover_backup = b2_file_path

        session.commit()
        print("done")

def image_backup_image():

    b2 = get_b2_resource()

    bucket_name = configs.b2.bucket_name

    with session_scope() as session:
        images = session.query(XiurenImage).filter(XiurenImage.backup_url == None).limit(10).all()

        for image in images:
            image_url = image.image_url
            #print(image_url)
            ext = image_url.split(".")[-1]
            b2_file_path = re.split('/', image_url.replace("https://", "").replace("http://", ""), maxsplit=1)[-1]
            print(b2_file_path)
            # check b2 file if exists
            if not key_exists(b2, bucket_name, b2_file_path):
                # not exist , download file and upload
                buf = get_image_content(image_url)
                if buf:
                    b2.Object(bucket_name, b2_file_path).put(Body=buf, ContentType=f"image/{ext}")
                else:
                    print(f"image download failed, {image_url}")
            else:
                #exists , skip upload,
                print(b2_file_path, "exists on b2, skip...")
            image.backup_url = b2_file_path
        session.commit()
        print("done")

if __name__ == "__main__":
    #image_backup_album()
    #image_backup_image()


    while True:
        with session_scope() as session:
            rows = session.query(func.count(XiurenAlbum.id)).filter(XiurenAlbum.cover_backup == None).scalar()
        if rows:
            image_backup_album()
            time.sleep(5)
        else:
            break

    while True:
        with session_scope() as session:
            rows = session.query(func.count(XiurenImage.id)).filter(XiurenImage.album_id == int(id), XiurenImage.is_enabled == 1).scalar()
        if rows:
            image_backup_image()
            time.sleep(5)
        else:
            break