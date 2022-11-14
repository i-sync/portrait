import scrapy
from xiuren.items import XiurenCategoryItem

class CategorySpider(scrapy.Spider):
    name = 'category'
    #allowed_domains = ['baidu.com']
    start_urls = ['https://www.xiurenb.cc/']

    custom_settings = {
        'ITEM_PIPELINES': {
            'xiuren.pipelines.XiurenCategoriesPipeline': 300,
        }
    }

    def parse(self, response):
        links = response.xpath("/html/body/div[1]/div/div[2]/ul/li[2]/ul//a")
        for l in links:
            item = XiurenCategoryItem()
            item["name"] = l.xpath("@href").extract_first().strip("/").lower()
            item["title"] = l.xpath("text()").extract_first().strip()
            print(item)
            yield item
