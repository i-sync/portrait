import scrapy


class ImageSpider(scrapy.Spider):
    name = 'image'
    allowed_domains = ['baidu.com']
    start_urls = ['http://baidu.com/']

    def parse(self, response):
        pass
