import os
import logging

import azure.cosmos.cosmos_client as CosmosClient

# COSMOSDB_URI = os.getenv('COSMOSDB_URI')
# COSMOSDB_KEY = os.getenv('COSMOSDB_KEY')
# DATABASE_NAME = os.getenv('COSMOSDB_DATABASE_NAME')
# CONTAINER_NAME = os.getenv('COSMOSDB_CONTAINER_NAME')

COSMOSDB_URI=os.getenv('COSMOSDB_URI')
COSMOSDB_KEY=os.getenv('COSMOSDB_KEY')
DATABASE_NAME="openai-ext-for-func"

# cosmosDB用のクラス
class CosmosService:
    def __init__(self, container_name: str):
        self.client = CosmosClient.CosmosClient(COSMOSDB_URI, {'masterKey': COSMOSDB_KEY})
        self.database = self.client.get_database_client(DATABASE_NAME)
        self.container = self.database.get_container_client(container_name)
        logging.info(f"Connected to CosmosDB: {COSMOSDB_URI}")

    def insert_data(self, data):
        self.container.upsert_item(data)
        logging.info(f"Inserted data into CosmosDB: {data}")
        
    def get_data(self, query):
        items = list(self.container.query_items(query=query, enable_cross_partition_query=True))
        logging.info(f"Got data from CosmosDB: {items}")
        return items

    def get_data_by_vector(self, vector):
        # vectorが適切な形式であることを確認する（例: リスト形式）
        formatted_vector = vector if isinstance(vector, list) else [vector]
        # クエリにLIMITを追加して結果の数を制限する
        query_with_limit = f'SELECT TOP 10 c.file_name, c.page_number, c.content, c.is_contain_image, c.image_blob_path, VectorDistance(c.content_vector, @embedding) AS SimilarityScore FROM c WHERE VectorDistance(c.content_vector, @embedding) > 0.5 ORDER BY VectorDistance(c.content_vector, @embedding)'
        items = list(self.container.query_items( 
                                                query=query_with_limit, 
                                                parameters=[ 
                                                    {"name": "@embedding", "value": formatted_vector} 
                                                ], 
                                                enable_cross_partition_query=True,
                                                max_item_count=10))
        logging.info(f"Got data from CosmosDB: {items}")
        return items

    def delete_data(self, item_id):
        return self.container.delete_item(item=item_id, partition_key=item_id)

    def update_data(self, query, data):
        items = list(self.container.query_items(query=query, enable_cross_partition_query=True))
        for item in items:
            self.container.replace_item(item, data)
        logging.info(f"Updated data in CosmosDB: {items}")
        return items