import minio
from datetime import timedelta
from .config import settings


class MinioStorage:
    def __init__(self):
        self.client = minio.Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

    def upload_file(self, file_path: str, object_name: str, bucket_name: str = "video"):
        self.client.fput_object(bucket_name, object_name, file_path)

    def delete_file(self, object_name: str, bucket_name: str = "video"):
        self.client.remove_object(bucket_name, object_name)

    def get_presigned_url(
        self, object_name: str, bucket_name: str = "video", expires: int = 3600
    ):
        url = self.client.presigned_get_object(
            bucket_name, object_name, expires=timedelta(seconds=expires)
        )

        return url

    def ensure_bucket(self, bucket_name: str = "video"):
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)


minio_storage = MinioStorage()
