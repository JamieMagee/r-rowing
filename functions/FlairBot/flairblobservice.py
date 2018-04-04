from os import environ

from azure.storage.blob import BlockBlobService, ContentSettings
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity


class FlairBlobService():

  container_name = 'blades'
  table_name = 'flair'
  flair_position_partition_key = 'flair-position'

  def __init__(self):
    self.blob_service = BlockBlobService(
        connection_string=environ['AzureWebJobsStorage'])
    self.blob_service.create_container(self.container_name)

    self.table_service = TableService(
        connection_string=environ['AzureWebJobsStorage'])
    self.table_service.create_table(self.table_name)

  def flair_exists(self, message_info):
    try:
      flair_entity = self.get_flair_entity(message_info)
      self.get_flair_position_entity(flair_entity)
      return True
    except:
      return False

  def get_flair_entity(self, flair_info):
    return self.table_service.get_entity(self.table_name, flair_info.club_name,
                                         flair_info.club_location)

  def get_flair_position_entity(self, flair_entity):
    return self.table_service.get_entity(
        self.table_name, self.flair_position_partition_key, flair_entity.path)
