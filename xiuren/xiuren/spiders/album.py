import re, os, sys, time, random
sys.path.append("..")
import scrapy
from threading import RLock
from bs4 import BeautifulSoup
from app.library.models import session_scope, XiurenCategory
from xiuren.items import XiurenAlbumItem

rlock = RLock()

class AlbumSpider(scrapy.Spider):
    name = 'album'
    #allowed_domains = ['baidu.com']
    base_url = "https://www.xiurenb.net"
    # page_number = 1
    start_urls = []

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'xiuren.middlewares.XiurenAlbumMiddleware': 500,
            'xiuren.middlewares.XiurenProxyMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'xiuren.pipelines.XiurenAlbumPipeline': 300,
        }
    }

    def __init__(self):
        super().__init__()
        with session_scope() as session:
            categories = session.query(XiurenCategory).filter(XiurenCategory.is_enabled == 1).all()
            for c in categories:
                self.start_urls.append(f"{self.base_url}/{c.name}/")
                # break

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"page_number": 1})
    
    def sub_detail_parse(self, response):
        # time.sleep(random.random())
        item = response.meta["item"]
        pages = response.meta["pages"]
        
        images = response.xpath("//div[@class='content']/p/img")
        for img in images:
            link = img.xpath("@src").extract_first()
            item["images"].append(f"{self.base_url}{link}")

        rlock.acquire()
        if len(pages):
            link = pages.pop(0)
            rlock.release()
            yield scrapy.Request(url = f"{self.base_url}{link}", callback=self.sub_detail_parse, meta={"item": item, "pages": pages})
        else:
            rlock.release()
            yield item

    def detail_parse(self, response):
        # time.sleep(random.random())
        item = response.meta["item"]
        title = response.xpath("/html/head/meta[@name='description']/@content").extract_first()
        keywords = response.xpath("/html/head/meta[@name='keywords']/@content").extract_first()
        date = response.xpath("//div[@class='item_info']/div/span[2]/text()").extract_first()
        digest = response.xpath("//div[@class='item_title']/h1/text()").extract_first()
        description = response.xpath("//div[@class='jianjie']/text()").extract_first()
        cover = response.xpath("//div[@class='content']/p/img[1]/@src").extract_first()

        item["title"] = title
        item["tags"] = keywords.split(",")[1:]
        item["origin_created_at"] = time.mktime(time.strptime(date, "%Y.%m.%d"))
        item["digest"] = digest
        item["description"] = ' '.join(description.split())
        item["origin_link"] = response.request.url
        item["cover"] = f"{self.base_url}{cover}"
        item["images"] = []

        images = response.xpath("//div[@class='content']/p/img")
        for img in images:
            link = img.xpath("@src").extract_first()
            item["images"].append(f"{self.base_url}{link}")

        pages = response.xpath("(//div[@class='page'])[1]/a/@href").extract()[1:-1]
        link = pages.pop(0)
        yield scrapy.Request(url = f"{self.base_url}{link}", callback=self.sub_detail_parse, meta={"item": item, "pages": pages})
            
        # yield item

    def parse(self, response):
        # time.sleep(random.random())
        category_name = response.request.url.split('/')[-2]

        totals = response.xpath("(//div[@class='page'])[1]/span/strong/text()").extract_first()
        totals = int(totals) if totals and totals.isdigit() else 0
        last_page = int(totals/20) if totals % 20 == 0 else int(totals/20) + 1
        lis = response.xpath("//ul[contains(@class, 'update_area_lists cl')]/li")
        for li in lis:
            link = li.xpath("./a/@href").extract_first()
            author = li.xpath("./a/div/span/text()").extract_first()
            item = XiurenAlbumItem()
            item["origin_link"] = link
            item["author"] = author
            item["category_name"] = category_name
            yield scrapy.Request(url = f"{self.base_url}{link}", callback=self.detail_parse, meta={"item": item, "request_type": "album"})
            

        page_number = response.meta["page_number"] if "page_number" in response.meta else 1
        page_number += 1
        if page_number <= last_page:
            next_url = f"{self.base_url}/{category_name}/index{page_number}.html"
            print(category_name, page_number, last_page, "next page", next_url)
            yield scrapy.Request(url = next_url, callback=self.parse, meta={"page_number": page_number})