from os import environ
from os.path import splitext

from azure.storage.blob import BlockBlobService, ContentSettings
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity


class FlairStorageService():

    container_name = 'blades'
    table_name = 'flair'
    png_content_type = ContentSettings(content_type='image/png')

    def __init__(self, name, src):
        self.path, _ = splitext(src.split("/blades/")[1])
        self.name = name

        self.blob_service = BlockBlobService(
            connection_string=environ['AzureWebJobsStorage']
        )
        self.blob_service.create_container(self.container_name)

        self.table_service = TableService(
            connection_string=environ['AzureWebJobsStorage']
        )
        self.table_service.create_table(self.table_name)

    def __upload_image__(self, blob, blob_name):
        self.blob_service.create_blob_from_bytes(
            self.container_name,
            blob_name,
            blob.getvalue(),
            content_settings=self.png_content_type
        )

    def upload_original(self, img):
        blob_name = f'original/{self.path}'
        self.__upload_image__(img, blob_name)

    def upload_flair(self, img):
        blob_name = f'flair/{self.path}'
        self.__upload_image__(img, blob_name)

    def create_table_row(self):
        entity = Entity()
        entity.PartitionKey = 'blob'
        entity.RowKey = self.name
        entity.path = self.path
        self.table_service
