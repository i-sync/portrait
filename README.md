# 美女写真

使用 scrapy 爬取 xiurenb.net写真网站数据，建立写真网站，并不下载图片

## Testing
uvicorn app.main:app --host 0.0.0.0 --port=8200

## Refer
> [https://github.com/selwin/python-user-agents](https://github.com/selwin/python-user-agents)

## Scrapy
cd root/xiuren
run `scrapy crawl album`

## Check proxy list
run `python3 /app/library/tools.py`