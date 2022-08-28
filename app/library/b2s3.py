#! /bin/bash

from email.headerregistry import ContentTypeHeader
import io
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

from app.library.config import configs


endpoint = configs.b2.endpoint
key_id = configs.b2.application_key_id
application_key = configs.b2.application_key

# Return a boto3 client object for B2 service
def get_b2_client():
    b2_client = boto3.client(service_name='s3',
                    endpoint_url=endpoint,                # Backblaze endpoint
                    aws_access_key_id=key_id,              # Backblaze keyID
                    aws_secret_access_key=application_key) # Backblaze applicationKey
    return b2_client


# Return a boto3 resource object for B2 service
def get_b2_resource():
    b2 = boto3.resource(service_name='s3',
            endpoint_url=endpoint,                # Backblaze endpoint
            aws_access_key_id=key_id,              # Backblaze keyID
            aws_secret_access_key=application_key, # Backblaze applicationKey
            config = Config(
                signature_version='s3v4',
            ))
    return b2

def key_exists(b2, bucket,  key):

    try:
        b2.Object(bucket, key).load()
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            # The object does not exist.
            return False
        else:
            # Something else has gone wrong.
            raise
    else:
        # The object does exist.
        return True