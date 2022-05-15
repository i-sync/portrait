# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os, sys, time
sys.path.append("..")
from itemadapter import ItemAdapter
from app.library.models import session_scope, XiurenAlbum, XiurenImage, XiurenCategory, XiurenTag

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
        print(item)
        return item
        
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