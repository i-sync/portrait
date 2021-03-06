# coding=UTF-8
import os
import sys


from sqlalchemy import func, desc

sys.path.append('../')
from app.library.config import configs
from app.library.page import Page
from app.library.models import session_scope, XiurenAlbum, XiurenCategory


def generate_sitemap_category():
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{configs.meta.site_url}</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>'''

    # category
    with session_scope() as session:
        categories = session.query(XiurenCategory).filter(XiurenCategory.is_enabled == 1).all()
        for category in categories:
            item = f'''
    <url>
        <loc>{configs.meta.site_url}/{category.name}</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>'''
            sitemap += item

    sitemap += '''
</urlset>'''

    with open("../sitemap.xml", "w+", encoding="utf-8") as f:
        f.writelines(sitemap)


def generate_sitemap_detail(offset, limit):

    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'''

    # article detail page
    with session_scope() as session:
        albums = session.query(XiurenAlbum).filter(XiurenAlbum.is_enabled == 1).limit(limit).offset(offset).all()

        categories = session.query(XiurenCategory).filter(XiurenCategory.is_enabled == 1).all()

        for album in albums:
            category = next((x for x in categories if x.id == album.category_id), None)
            item = f'''
    <url>
        <loc>{configs.meta.site_url}/{category.name}/{album.id}</loc>
        <changefreq>daily</changefreq>
        <priority>0.5</priority>
    </url>'''
            sitemap += item

    sitemap += '''
</urlset>'''

    with open(f"../sitemap-{offset}-{limit}.xml", "w+", encoding="utf-8") as f:
        f.writelines(sitemap)


if __name__=="__main__":
    generate_sitemap_category()

    rows = 0
    with session_scope() as session:
        rows = session.query(func.count(XiurenAlbum.id)).filter(XiurenAlbum.is_enabled == 1).scalar()

    page = Page(rows, page_index=1, page_size=5000)
    for i in range(1, page.page_count + 1):

        page = Page(rows, page_index=i, page_size=5000)
        generate_sitemap_detail(page.offset, page.limit)

    print("Done")
