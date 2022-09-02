#! /usr/bin

import os, time
from b2sdk.v2 import *
from app.library.config import configs

key_id = configs.b2.application_key_id
application_key = configs.b2.application_key
default_bucket_name = configs.b2.bucket_name

def get_b2_api():
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account("production", key_id, application_key)

    return b2_api

def get_b2_bucket(bucket_name = None):
    global default_bucket_name
    if bucket_name:
        default_bucket_name = bucket_name

    b2_api = get_b2_api()
    b2_bucket = b2_api.get_bucket_by_name(default_bucket_name)
    return b2_bucket