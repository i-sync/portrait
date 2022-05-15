#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import integer, tile
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Time, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from contextlib import contextmanager

from app.library.config import configs

engine = create_engine(f"mysql+pymysql://{configs.database.user}:{configs.database.password}@{configs.database.host}:{configs.database.port}/{configs.database.database}", pool_recycle=3600)
DBSession = sessionmaker(bind=engine)
Base = declarative_base()

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = DBSession()
    try:
        yield session
        #session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class XiurenAlbum(Base):
    __tablename__ = "xiuren_album"
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    digest = Column(String(500))
    description = Column(String(2048))
    category_id = Column(Integer)
    tags = Column(String(100))
    cover = Column(String(200))
    author = Column(String(100))
    view_count = Column(Integer)
    origin_link = Column(String(200))
    origin_created_at = Column(Float)
    created_at = Column(Float)
    updated_at = Column(Float)
    is_enabled = Column(Boolean)

class XiurenImage(Base):
    __tablename__ = "xiuren_images"
    id = Column(Integer, primary_key=True)
    album_id = Column(Integer)
    image_url = Column(String(200))
    created_at = Column(Float)
    updated_at = Column(Float)
    is_enabled = Column(Boolean)

class XiurenCategory(Base):
    __tablename__ = "xiuren_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    title = Column(String(100))
    created_at = Column(Float)
    updated_at = Column(Float)
    is_enabled = Column(Boolean)

class XiurenTag(Base):
    __tablename__ = "xiuren_tags"
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    created_at = Column(Float)
    updated_at = Column(Float)
    is_enabled = Column(Boolean)
