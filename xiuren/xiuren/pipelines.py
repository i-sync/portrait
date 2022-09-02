# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import io, os, sys, time
sys.path.append("..")
from itemadapter import ItemAdapter
from app.library.config import configs
from app.library.models import session_scope, XiurenAlbum, XiurenImage, XiurenCategory, XiurenTag

from app.library.b2s3 import get_b2_resource, key_exists
from app.library.b2 import get_b2_api, get_b2_bucket

class XiurenAlbumPipeline:
    def process_item(self, item, spider):
        print(item)
        if not len(item["images"]):
            print("album doesn't contains images, skip.", item["title"], item["origin_link"])
            return
        with session_scope() as session:
            album = session.query(XiurenAlbum).filter(XiurenAlbum.title == item["title"]).first()
        if album:
            print("album already exists, skip.", item["title"], item["origin_link"])
        else:
            with session_scope() as session:
                category = session.query(XiurenCategory).filter(XiurenCategory.name == item["category_name"]).first()
            tag_ids = []
            commit_flag = False
            with session_scope() as session:
                for t in item["tags"]:
                    tag = session.query(XiurenTag).filter(XiurenTag.title == t).first()
                    if tag:
                        tag_ids.append(str(tag.id))
                    else:
                        commit_flag = True
                        tag = XiurenTag()
                        tag.title = t
                        tag.is_enabled = 1
                        tag.created_at = time.time()
                        tag.updated_at = time.time()
                        session.add(tag)
                        session.flush()
                        tag_ids.append(str(tag.id))
                if commit_flag:
                    session.commit()
                print("tags commit!")

            album = XiurenAlbum()
            album.title = item["title"]
            album.digest = item["digest"]
            album.description = item["description"]
            album.cover = item["cover"]
            album.author = item["author"]
            album.origin_link = item["origin_link"]
            album.origin_created_at = item["origin_created_at"]
            album.category_id = category.id
            album.tags = ','.join(tag_ids)
            album.view_count = 0
            album.created_at = time.time()
            album.updated_at = time.time()
            album.is_enabled = 1

            with session_scope() as session:
                session.add(album)
                session.flush()
                album_id = album.id
                for img in item["images"]:
                    image = XiurenImage()
                    image.album_id = album_id
                    image.image_url = img
                    image.created_at = time.time()
                    image.updated_at = time.time()
                    image.is_enabled = 1

                    session.add(image)

                session.commit()
                print("album and image commit.")


        return item

class XiurenImagePipeline:
    def process_item(self, item, spider):
        if not item:
            return

        print(item["id"], item["ct"], item["b2_key"], item["ext"])
        #return item

        ''' boto3
        b2 = get_b2_resource()
        bucket_name = configs.b2.bucket_name

        id = item["id"]
        ct = item["ct"]
        buf = io.BytesIO(item["content"])
        ext = item["ext"]
        b2_key = item["b2_key"]
        b2.Object(bucket_name, b2_key).put(Body=buf, ContentType=f"image/{ext}")
        print(f"image upload b2 finish, b2_key:{b2_key}")

        if ct == "album":
            with session_scope() as session:
                album = session.query(XiurenAlbum).filter(XiurenAlbum.id == id).first()
                if album:
                    album.cover_backup = b2_key
                else:
                    print(f"album not found, id:{id}")
                session.commit()
        elif ct == "image":
            with session_scope() as session:
                image = session.query(XiurenImage).filter(XiurenImage.id == id).first()
                if image:
                    image.backup_url = b2_key
                else:
                    print(f"image not found, id:{id}")
                session.commit()
        '''

        # b2sdk
        bucket = get_b2_bucket()

        id = item["id"]
        ct = item["ct"]
        buf = item["content"]
        ext = item["ext"]
        b2_key = item["b2_key"]

        bucket.upload_bytes(buf, b2_key, content_type=f"image/{ext}")
        print(f"image upload b2 finish, b2_key:{b2_key}")

        if ct == "album":
            with session_scope() as session:
                album = session.query(XiurenAlbum).filter(XiurenAlbum.id == id).first()
                if album:
                    album.cover_backup = b2_key
                else:
                    print(f"album not found, id:{id}")
                session.commit()
        elif ct == "image":
            with session_scope() as session:
                image = session.query(XiurenImage).filter(XiurenImage.id == id).first()
                if image:
                    image.backup_url = b2_key
                else:
                    print(f"image not found, id:{id}")
                session.commit()

class XiurenCategoriesPipeline:

    def process_item(self, item, spider):
        category = XiurenCategory()
        category.name = item["name"]
        category.title = item["title"]
        category.created_at = time.time()
        category.updated_at = time.time()
        category.is_enabled = 1
        with session_scope() as session:
            session.add(category)
            session.commit()
        return item