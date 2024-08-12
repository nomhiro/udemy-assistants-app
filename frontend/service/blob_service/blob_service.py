import os
import base64

from azure.storage.blob import BlobServiceClient

# 環境変数からAzure Storageの情報を取得
# AZURE_STORAGE_CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
# AZURE_STORAGE_CONTAINER_NAME = os.environ['AZURE_STORAGE_CONTAINER_NAME']
AZURE_STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=saalmragdocs;AccountKey=UP7CdMZosnsGy0rAmW0m30yY302uXkvwY4nJDqnGaU9VU0cuXcKbx7UEsDOIC3bLt6330lUWKY2p+AStaTRccA==;EndpointSuffix=core.windows.net"
AZURE_STORAGE_CONTAINER_NAME = "images"

# ファイルを取得してbase64でエンコードする関数
def get_base64_file(file_path):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=AZURE_STORAGE_CONTAINER_NAME, blob=file_path)

    # Blobからデータをダウンロード
    stream = blob_client.download_blob()
    data = stream.readall()

    # データをbase64でエンコード
    encoded_data = base64.b64encode(data).decode('utf-8')
    return encoded_data