# coding=UTF-8
import os
import sys

sys.path.append('../')
from app.library.config import configs
from app.library.models import session_scope, ArticleInfo, Tags, PublicAccount


def generate_sitemap():
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{configs.meta.site_url}</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>'''

    # public account
    with session_scope() as session:
        public_accounts = session.query(PublicAccount).all()
        for account in public_accounts:
            item = f'''
    <url>
        <loc>{configs.meta.site_url}/account/{account.fakeid}/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>'''
            sitemap += item

    # article detail page
    with session_scope() as session:
        articles = session.query(ArticleInfo).filter(ArticleInfo.is_crawled == 1, ArticleInfo.is_enabled == 1).all()
        for article in articles:
            item = f'''
    <url>
        <loc>{configs.meta.site_url}/article/{article.id}/</loc>
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