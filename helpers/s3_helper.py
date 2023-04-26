import io
import logging
from typing import TYPE_CHECKING, Optional

import boto3

import config.s3_config
from helpers.s3_paths import append_prefix

ACL_PRIVATE = 'private'
ACL_PUBLIC_READ = 'public-read'

if TYPE_CHECKING:
    from mypy_boto3_s3.service_resource import S3ServiceResource, Bucket
else:
    S3Client = object
    S3ServiceResource = object
    Bucket = object


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class S3Helper(metaclass=Singleton):
    def __init__(self):
        self.session = boto3.session.Session(
            aws_access_key_id=config.s3_config.s3_access_key_id,
            aws_secret_access_key=config.s3_config.s3_secret_access_key,
        )

    def get_resource(self) -> S3ServiceResource:
        resource: S3ServiceResource = self.session.resource(
            's3',
            endpoint_url=config.s3_config.s3_endpoint,
            use_ssl=config.s3_config.s3_use_ssl,
        )
        return resource

    def s3_download_file(
            self,
            file_path_in_bucket,
            s3_bucket_name: str = config.s3_config.s3_bucket_name,
            s3_prefix: Optional[str] = config.s3_config.s3_prefix,
    ) -> bytes:
        bucket: Bucket = self.get_resource().Bucket(s3_bucket_name)
        result_path_in_bucket = append_prefix(path=file_path_in_bucket, prefix=s3_prefix)
        with io.BytesIO() as buffer:
            bucket.download_fileobj(Key=result_path_in_bucket, Fileobj=buffer)
            result = buffer.getvalue()
        logging.warning(
            f'File downloaded from bucket={s3_bucket_name} with key={result_path_in_bucket} data[:10]={result[:min(10, len(result))]}')
        return result
