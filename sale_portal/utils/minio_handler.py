import logging
from datetime import timedelta

from minio import Minio

from sale_portal import settings

logger = logging.getLogger()


class MinioHandler():
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if not MinioHandler.__instance:
            MinioHandler.__instance = MinioHandler()
        return MinioHandler.__instance

    def __init__(self):
        self.minio_url = settings.MINIO_AUTH['url']
        self.access_key = settings.MINIO_AUTH['access_key']
        self.secret_key = settings.MINIO_AUTH['secret_key']
        self.bucket_name = settings.MINIO_AUTH['bucket_name']
        self.client = Minio(
            self.minio_url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )
        self.make_bucket()

    def make_bucket(self) -> str:
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
        return self.bucket_name

    def presigned_get_object(self, bucket_name, object_name):
        # Request URL expired after 7 days
        url = self.client.presigned_get_object(
            bucket_name=bucket_name,
            object_name=object_name,
            expires=timedelta(days=7)
        )
        return url

    def check_file_name_exists(self, bucket_name, file_name):
        try:
            self.client.stat_object(bucket_name=bucket_name, object_name=file_name)
            return True
        except Exception as e:
            logger.debug(e)
            return False


def from_file_type_to_mime_type(file_type: str) -> str:
    FILE_TYPE_TO_MIME = {
        'rar': 'application/vnd.rar',
        'zip': 'application/zip',
        'png': 'image/png',
        'pdf': 'application/pdf',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }

    return FILE_TYPE_TO_MIME.get(file_type, 'application/octet-stream')
