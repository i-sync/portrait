"""
 Target: https://news.ycombinator.com/
 pip install aiofiles
"""
import aiofiles

from ruia import Item, TextField, AttrField, Spider


class HackerNewsItem(Item):
    target_item = TextField(css_select='tr.athing')
    title = TextField(css_select='a.storylink')
    url = AttrField(css_select='a.storylink', attr='href')


class HackerNewsSpider(Spider):
    concurrency = 2
    start_urls = [f'https://news.ycombinator.com/news?p={index}' for index in range(3)]

    async def parse(self, response):
        async for item in HackerNewsItem.get_items(html=await response.text()):
            yield item

    async def process_item(self, item: HackerNewsItem):
        """Ruia build-in method"""
        async with aiofiles.open('./hacker_news.txt', 'a') as f:
            await f.write(str(item.title) + '\n')

if __name__ == '__main__':
    HackerNewsSpider.start()