from google.cloud import storage
from google.oauth2 import service_account
import datetime
import base64
import io
from configs.config import settings

class CloudStorageService:
    def __init__(self, bucketname=settings.SALES_BUCKET):
        self.bucketname = bucketname  # Define bucketname as an instance variable
        self.projectname = settings.PROJECT_NAME
        self.credentials = service_account.Credentials.from_service_account_file(settings.CREDS_FILE)
        
    async def upload(self, filename, file):
        storage_client = storage.Client(
            self.projectname)
        bucket = storage_client.get_bucket(self.bucketname)
        blob = bucket.blob(filename)
        file.file.seek(0)
        blob.upload_from_file(file.file)

    async def upload_from_bytes(self, filename, file):
        storage_client = storage.Client(
            self.projectname)
        bucket = storage_client.get_bucket(self.bucketname)
        blob = bucket.blob(filename)
        blob.upload_from_file(io.BytesIO(file))

    async def get_signed_url(self, filename):
        storage_client = storage.Client(
            self.projectname, credentials=self.credentials)
        bucket = storage_client.get_bucket(self.bucketname)
        blob = bucket.blob(filename)
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=15),
            method="GET",
        )
        return url

    async def get_base64_data(self, filename):
        storage_client = storage.Client(
            self.projectname)
        bucket = storage_client.bucket(self.bucketname)
        blob = bucket.blob(filename)
        file_content = blob.download_as_string()
        return base64.b64encode(file_content).decode("utf-8")

    async def get_string_data(self, filename):
        storage_client = storage.Client(
            self.projectname)
        bucket = storage_client.bucket(self.bucketname)
        blob = bucket.blob(filename)
        file_content = blob.download_as_string().decode("utf-8")
        return file_content

    async def get_bytes_data(self, filename):
        storage_client = storage.Client(
            self.projectname)
        bucket = storage_client.bucket(self.bucketname)
        blob = bucket.blob(filename)
        file_content = blob.download_as_bytes()
        return file_content
    
    async def check_if_file_exist(self, filename):
        storage_client = storage.Client(
            self.projectname)
        bucket = storage_client.bucket(self.bucketname)
        # blob = bucket.blob(filename)
        exist=storage.Blob(bucket=bucket,name=filename).exists(storage_client)
        return exist
    
    async def remove(self, filename):
        storage_client = storage.Client(
            self.projectname)
        bucket = storage_client.bucket(self.bucketname)
        blob = bucket.blob(filename)
        blob.delete()
