#!/usr/bin/python
# -*- coding: utf-8 -*-

import json, time, random
import requests
from base64 import b64decode
from typing import Optional

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException

from starlette.responses import Response, RedirectResponse
from sqlalchemy import func, desc
from sqlalchemy.sql import text

from user_agents import parse

from app.library.models import session_scope, XiurenAlbum, XiurenCategory, XiurenImage, XiurenTag
from app.routers import login, logs
from app.routers.login import manager
from app.library.tools import date_filter, datetime_filter, COLORS
from app.library.page import Page, PageAll, get_page_index
from app.library.logger import logger
from app.library.config import configs

app = FastAPI()
app.include_router(login.router)
app.include_router(logs.router)


templates = Jinja2Templates(directory="templates")
# add custom filter
templates.env.filters["datetime"] = datetime_filter
templates.env.filters["date"] = date_filter

app.mount("/static", StaticFiles(directory="static"), name="static")


manager.useRequest(app)

class NotAuthenticatedException(Exception):
    pass

# these two argument are mandatory
def exc_handler(request, exc):
    return RedirectResponse(url='/login')

# This will be deprecated in the future
# set your exception when initiating the instance
# manager = LoginManager(..., custom_exception=NotAuthenticatedException)
manager.not_authenticated_exception = NotAuthenticatedException
# You also have to add an exception handler to your app instance
app.add_exception_handler(NotAuthenticatedException, exc_handler)

MENU = {
    '/': 'Home',
    #'/page/logs': '日志'
}

def check_login(request: Request):
    user = request.state.user
    if user is None:
        raise NotAuthenticatedException()
    else:
        return user

def get_category():
    with session_scope() as session:
        categories = session.query(XiurenCategory).filter(XiurenCategory.is_enabled == 1).all()
        session.expunge_all()
    # print(categories)
    return categories

def parse_user_agent(request: Request):
    user_agent = parse(request.headers.get("user-agent"))
    request.user_agent = user_agent

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, page = "1", order = "new"):
    parse_user_agent(request)
    categories = get_category()
    page_index = get_page_index(page)
    with session_scope() as session:
        #rows = session.query(func.count(XiurenAlbum.id)).filter(XiurenAlbum.is_enabled == 1).scalar()
        page = Page(200, page_index)
        albums = session.query(XiurenAlbum).filter(XiurenAlbum.is_enabled == 1).order_by(func.random()).offset(page.offset).limit(page.limit).all()
        for album in albums:
            album.category = next(x for x in categories if x.id == album.category_id)
        tops = session.query(XiurenAlbum).filter(XiurenAlbum.is_enabled == 1).order_by(desc(XiurenAlbum.view_count)).limit(10).all()
        for album in tops:
            album.category = next(x for x in categories if x.id == album.category_id)
    data = {
        "menu": MENU,
        "page": page,
        "categories": get_category(),
        "tops": tops,
        "albums": albums,
        "url": request.url,
        "meta": configs.meta,
        "cover": tops[0].cover if len(tops) else f"{configs.meta.site_url}/static/images/cover.jpg",
        "friendly_link": configs.friendly_link,
        "keywords": configs.meta.keywords,
        "description": configs.meta.description
    }
    return templates.TemplateResponse("index.html", {"request": request, "data": data})


@app.get("/search", response_class=HTMLResponse)
async def search(s, request: Request, page = "1", order = "new"):
    if not s:
        return RedirectResponse("/")
    parse_user_agent(request)
    page_index = get_page_index(page)
    categories = get_category()
    with session_scope() as session:
        rows = session.query(func.count(XiurenAlbum.id)).filter(XiurenAlbum.title.contains(s), XiurenAlbum.is_enabled == 1).scalar()
        page = Page(rows, page_index)
        albums = session.query(XiurenAlbum).filter(XiurenAlbum.title.contains(s), XiurenAlbum.is_enabled == 1).offset(page.offset).limit(page.limit).all()
        for album in albums:
            album.category = next(x for x in categories if x.id == album.category_id)        
        tops = session.query(XiurenAlbum).filter(XiurenAlbum.is_enabled == 1).order_by(desc(XiurenAlbum.view_count)).limit(10).all()
        for album in tops:
            album.category = next(x for x in categories if x.id == album.category_id)
    data = {
        "menu": MENU,
        "page": page,
        "categories": categories,
        "tops": tops,
        "albums": albums,
        "location": "搜索结果",
        "url": request.url,
        "meta": configs.meta,
        "cover": tops[0].cover if len(tops) else f"{configs.meta.site_url}/static/images/cover.jpg",
        "friendly_link": configs.friendly_link,
        "keywords": configs.meta.keywords,
        "description": configs.meta.description
    }
    return templates.TemplateResponse("other.html", {"request": request, "data": data})

@app.get("/sort/{order}", response_class=HTMLResponse)
async def sort(order, request: Request):
    if not order:
        return RedirectResponse("/")
    parse_user_agent(request)
    categories = get_category()
    with session_scope() as session:
        if order == "new":
            albums = session.query(XiurenAlbum).filter(XiurenAlbum.is_enabled == 1).order_by(desc(XiurenAlbum.origin_created_at)).limit(50).all()
        else:            
            albums = session.query(XiurenAlbum).filter(XiurenAlbum.is_enabled == 1).order_by(desc(XiurenAlbum.view_count)).limit(50).all()
        for album in albums:
            album.category = next(x for x in categories if x.id == album.category_id)        
        tops = session.query(XiurenAlbum).filter(XiurenAlbum.is_enabled == 1).order_by(desc(XiurenAlbum.view_count)).limit(10).all()
        for album in tops:
            album.category = next(x for x in categories if x.id == album.category_id)
    data = {
        "menu": MENU,
        "categories": categories,
        "tops": tops,
        "albums": albums,
        "location": "最新" if order == "new" else "最热",
        "url": request.url,
        "meta": configs.meta,
        "cover": tops[0].cover if len(tops) else f"{configs.meta.site_url}/static/images/cover.jpg",
        "friendly_link": configs.friendly_link,
        "keywords": configs.meta.keywords,
        "description": configs.meta.description
    }
    return templates.TemplateResponse("other.html", {"request": request, "data": data})


@app.get("/{category}", response_class=HTMLResponse)
async def category(category, request: Request, page = "1", order = "new"):
    parse_user_agent(request)
    categories = get_category()
    category = next((x for x in categories if x.name == category), None)
    if not category:
        return RedirectResponse("/")
    page_index = get_page_index(page)
    with session_scope() as session:
        rows = session.query(func.count(XiurenAlbum.id)).filter(XiurenAlbum.category_id == category.id, XiurenAlbum.is_enabled == 1).scalar()
        page = Page(rows, page_index)        
        
        albums = session.query(XiurenAlbum).filter(XiurenAlbum.category_id == category.id, XiurenAlbum.is_enabled == 1).offset(page.offset).limit(page.limit).all()
        for album in albums:
            album.category = next(x for x in categories if x.id == album.category_id)
        tops = session.query(XiurenAlbum).filter(XiurenAlbum.category_id == category.id, XiurenAlbum.is_enabled == 1).order_by(desc(XiurenAlbum.view_count)).limit(10).all()
        for album in tops:
            album.category = next(x for x in categories if x.id == album.category_id)

    data = {
        "menu": MENU,
        "page": page,
        "categories": categories,
        "category": category,
        "tops": tops,
        "albums": albums,
        "url": request.url,
        "meta": configs.meta,
        "cover": tops[0].cover if len(tops) else f"{configs.meta.site_url}/static/images/cover.jpg",
        "friendly_link": configs.friendly_link,
        "keywords": f"{configs.meta.keywords}, {category.title}" if category else configs.meta.keywords,
        "description": f"{configs.meta.description}, {category.title}" if category else configs.meta.description
    }
    return templates.TemplateResponse("index.html", {"request": request, "data": data})


@app.get("/{category}/{id}", response_class=HTMLResponse)
async def article(category, id, request: Request, page = "1"):
    parse_user_agent(request)
    categories = get_category()
    page_index = get_page_index(page)
    with session_scope() as session:
        album = session.query(XiurenAlbum).filter(XiurenAlbum.id == int(id), XiurenAlbum.is_enabled == 1).first()
        album.category = next(x for x in categories if x.id == album.category_id)
        # if album:
        #     session.expunge(album)
        tags = session.query(XiurenTag).filter(XiurenTag.id.in_(eval(album.tags))).all()

        rows = session.query(func.count(XiurenImage.id)).filter(XiurenImage.album_id == int(id), XiurenImage.is_enabled == 1).scalar()
        page = PageAll(rows, page_index, page_size=3)

        images = session.query(XiurenImage).filter(XiurenImage.album_id == int(id), XiurenImage.is_enabled == 1).offset(page.offset).limit(page.limit).all()
        # if article_detail:
        #     session.expunge(article_detail)

    # r = requests.get(album.cover)
    # cover = r.history[-1].headers["Location"] if r.status_code == 200 and len(r.history) else f"{configs.meta.site_url}/static/images/cover.jpg"
    data = {
        "menu": MENU,
        "page": page,
        "categories": categories,
        "album": album,
        "tags": tags,
        "images": images,
        "url": request.url,
        "meta": configs.meta,
        "cover": album.cover,
        "friendly_link": configs.friendly_link,
        "keywords": ", ".join([x.title for x in tags])
    }
    return templates.TemplateResponse("article.html", {"request": request, "data": data})

@app.get("/plus/count/{id}", response_class=HTMLResponse)
async def count(id, request: Request):
    if not id or not id.isdigit():
        return "document.write('0');"
    view_count = 0
    with session_scope() as session:
        album = session.query(XiurenAlbum).filter(XiurenAlbum.id == int(id), XiurenAlbum.is_enabled == 1).first()
        if album:
            album.view_count += 1
            view_count = album.view_count
            session.commit()
    return f"document.write('{view_count}');"

