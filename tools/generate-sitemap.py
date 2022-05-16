# coding=UTF-8
import os
import sys

sys.path.append('../')
from app.library.config import configs
from app.library.models import session_scope, XiurenAlbum, XiurenCategory


def generate_sitemap():
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

    # article detail page
    with session_scope() as session:
        albums = session.query(XiurenAlbum).filter(XiurenAlbum.is_enabled == 1).all()
        for album in albums:
            category = next((x for x in categories if x.id == album.category_id), None)
            item = f'''
    <url>
        <loc>{configs.meta.site_url}/{category.name}/{album.id}</loc>
        <changefreq>monthly</changefreq>
        <priority>0.5</priority>
    </url>'''
            sitemap += item
    sitemap += '''
</urlset>'''

    with open("../sitemap.xml", "w+", encoding="utf-8") as f:
        f.writelines(sitemap)

if __name__=="__main__":
    generate_sitemap()