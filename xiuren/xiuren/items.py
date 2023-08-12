# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class XiurenAlbumItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    digest = scrapy.Field()
    description = scrapy.Field()
    #category_id = scrapy.Field()
    category_name = scrapy.Field()
    tags = scrapy.Field()
    cover = scrapy.Field()
    cover_backup = scrapy.Field()
    author = scrapy.Field()
    origin_link = scrapy.Field()
    origin_created_at = scrapy.Field()
    image_urls = scrapy.Field()
    image_paths = scrapy.Field()

class XiurenCategoryItem(scrapy.Item):
    name = scrapy.Field()
    title = scrapy.Field()

class XiurenImageItem(scrapy.Item):
    b2_key = scrapy.Field()
    content = scrapy.Field()
    id = scrapy.Field()
    ct = scrapy.Field()
    ext = scrapy.Field()
    new_image_path = scrapy.Field()