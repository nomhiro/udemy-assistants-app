import streamlit as st
import logging
from io import BytesIO
import logging
import tempfile
import base64
import json
from urllib.parse import urlparse
from PIL import Image
import pymupdf
import os

from openai import AzureOpenAI
from azure.storage.blob import BlobServiceClient

from service.openai_service.openai_service import AzureOpenAIService
from service.cosmos_service.cosmos_service import CosmosService
from domain.obj_cosmos_page import CosmosPageObj
from call_api.call_func_aoai import api_embedding

logging.basicConfig(level=logging.INFO)

STR_AI_SYSTEMMESSAGE = """
##役割
- 画像内の情報を、Markdown形式に整理する役割です。"抜けもれなく"テキストに変換してください。

##制約条件
- 出力内容は2000文字以内にまとめなさい。
- 図や表が含まれる場合、図や表の内容を理解できるように説明する文章にしなさい。
- 数値情報を繰り返し出力してはいけません。
- 図や表に数値情報が多量に含まれる場合、数値情報の記載はする必要がありません。

##回答形式##
{
    "content":"画像をテキストに変換した文字列",
    "keywords": "カンマ区切りのキーワード群",
    "is_contain_image": "図や表などの画像で保存しておくべき情報が含まれている場合はtrue、それ以外はfalse"
}

##記載情報##
- content: 画像内の情報はcontentに記載してください。画像内の情報を漏れなく記載してください。
- keywords: 画像内の情報で重要なキーワードをkeywordsに記載してください。カンマ区切りで複数記載可能です。
- is_contain_image: 図や表などの画像で保存しておくべき情報が含まれている場合はtrue、それ以外はfalseを記載してください。
"""
STR_AI_USERMESSAGE = """画像の内容を用いて回答しなさい。Json形式でのみ回答してください。"""
STR_SAMPLE_USERMESSAGE = """画像の内容を用いて回答しなさい。Json形式でのみ回答してください。"""
STR_SAMPLE_AIRESPONSE = """{
    "content":"画像をテキストに変換した文字列",
    "keywords": "word1, word2, word3"
}"""

BLOB_TRIGGER_PATH = "docs"

BLOB_CONTAINER_NAME_IMAGE = "images"
# BLOB_CONNECTION = os.getenv("BLOB_CONNECTION")
BLOB_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=saalmragdocs;AccountKey=UP7CdMZosnsGy0rAmW0m30yY302uXkvwY4nJDqnGaU9VU0cuXcKbx7UEsDOIC3bLt6330lUWKY2p+AStaTRccA==;EndpointSuffix=core.windows.net"

CONTAINER_NAME="vector-store"

aoai_client = AzureOpenAI(
    # azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    # api_key=os.getenv("AZURE_OPENAI_KEY"),
    # azure_endpoint="https://aoai-eastus-apimtest-001.openai.azure.com",
    # api_key="183101ec494c45aba62b7e1e18365b7f",
    azure_endpoint="https://aoai-rag.openai.azure.com",
    api_key="9b4e131d7074437eb977a79c9f31d1ad",
    api_version="2024-03-01-preview"
)
azure_openai_service = AzureOpenAIService(client=aoai_client)
cosmos_service = CosmosService(container_name=CONTAINER_NAME)
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION)

# PDFファイルをアップロードする
st.write("PDFファイルをアップロードしてください")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# uploaded_fileがある場合
if uploaded_file:

    file_name = uploaded_file.name

    # Create a temporary file
    temp_path = ""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
        temp.write(uploaded_file.read())
        temp_path = temp.name

    doc = pymupdf.open(temp_path)
    # ページ数をログに出力
    logging.info(f"🚀PDF Page count : {doc.page_count}")

    # ページごとにCosmosDBのアイテムを作成し、ページ画像がある場合はページの画像ファイルをBlobにを作成
    for page in doc:  # iterate through the pages
        logging.info(f"🚀Page Number: {page.number}")
        pix = page.get_pixmap()  # render page to an image
        # Convert the pixmap to a PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        binary_data = BytesIO()
        img.save(binary_data, format='PNG')
        binary_data.seek(0)
        base64_data = base64.b64encode(binary_data.getvalue()).decode()
        
        # OpenAIに推論させるためのメッセージを作成
        image_content = []
        image_content.append({
            "type": "image_url",
            "image_url": 
            {
                "url": f"data:image/jpeg;base64,{base64_data}"
            },
        })
        messages = []
        messages.append({"role": "system", "content": STR_AI_SYSTEMMESSAGE})
        messages.append({"role": "user", "content": STR_SAMPLE_USERMESSAGE})
        messages.append({"role": "user", "content": STR_SAMPLE_AIRESPONSE})
        messages.append({"role": "user", "content": STR_AI_USERMESSAGE})
        messages.append({"role": "user", "content": image_content})
        
        response = azure_openai_service.getChatCompletionJsonMode(messages, 0, 0)
        response_message = response.choices[0].message.content
        logging.info(f"🚀Response Output: {response_message}")
        
        # 回答をJSONに変換する
        output = json.loads(response_message)
        
        # contentをベクトル値に変換
        # content_vector = azure_openai_service.getEmbedding(output["content"])
        embedding = api_embedding(output["content"])
        
        # is_contain_imageがTrueの場合は、StorageAccountのBlobの"rag-images"に画像をアップロード
        if output["is_contain_image"]:
            # 格納するパスを生成。TriggerされたBlobのパスのフォルダとファイル名を、格納先フォルダにする。
            
            stored_image_path = file_name + "_page" + str(page.number) + ".png"
            
            blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME_IMAGE, blob=stored_image_path)
            blob_client.upload_blob(base64.b64decode(base64_data), overwrite=True)
            logging.info(f"🚀Uploaded Image to Blob: {stored_image_path}")
        
        # CosmosDBに登録するアイテムのオブジェクト
        cosmos_page_obj = CosmosPageObj(file_name=file_name,
                                        page_number=page.number,
                                        content=output["content"], 
                                        content_vector=embedding,
                                        keywords=output["keywords"],
                                        delete_flag=False,
                                        is_contain_image=output["is_contain_image"],
                                        image_blob_path=stored_image_path if output["is_contain_image"] else None)
        
        cosmos_service.insert_data(cosmos_page_obj.to_dict())