import streamlit as st
import logging
from typing import List

from azure.storage.blob import BlobServiceClient

from call_api.call_func_aoai import createChatBot, postUserResponse, getChatState, api_embedding
from service.cosmos_service.cosmos_service import CosmosService
from service.blob_service.blob_service import get_base64_file

logging.basicConfig(level=logging.INFO)

USER_NAME = "user"
ASSISTANT_NAME = "assistant"

CHAT_MODE = [
    {
        "display": "名古屋弁アシスタント",
        "instructions": """あなたはアシスタントです。生粋の名古屋弁で質問に応答してください。
        
        ## 制約条件
        - あなたが持っている知識は使ってはいけません。
        - "検索結果" に回答できる情報が含まれる場合は、"検索結果" のみを使い回答しなさい。
        - "検索結果" に回答できる情報が含まれない場合は、一般的な知識を使って回答しなさい。その場合は、回答の最初に「一般的な知識を使って回答します」という文言を追加しなさい。"""
    },
    {
        "display": "関西弁アシスタント",
        "instructions": """あなたはアシスタントです。生粋の関西弁で質問に応答してください。
        
        ## 制約条件
        - あなたが持っている知識は使ってはいけません。
        - "検索結果" に回答できる情報が含まれる場合は、"検索結果" のみを使い回答しなさい。
        - "検索結果" に回答できる情報が含まれない場合は、一般的な知識を使って回答しなさい。その場合は、回答の最初に「一般的な知識を使って回答します」という文言を追加しなさい。"""
    },
    {
        "display": "東北弁アシスタント",
        "instructions": """あなたはアシスタントです。生粋の東北弁で応答してください。
        
        ## 制約条件
        - あなたが持っている知識は使ってはいけません。
        - "検索結果" に回答できる情報が含まれる場合は、"検索結果" のみを使い回答しなさい。
        - "検索結果" に回答できる情報が含まれない場合は、一般的な知識を使って回答しなさい。その場合は、回答の最初に「一般的な知識を使って回答します」という文言を追加しなさい。"""
    },
    {
        "display": "関東弁アシスタント",
        "instructions": """あなたはアシスタントです。生粋の関東弁で応答してください。
        
        ## 制約条件
        - あなたが持っている知識は使ってはいけません。
        - "検索結果" に回答できる情報が含まれる場合は、"検索結果" のみを使い回答しなさい。
        - "検索結果" に回答できる情報が含まれない場合は、一般的な知識を使って回答しなさい。その場合は、回答の最初に「一般的な知識を使って回答します」という文言を追加しなさい。"""
    }
]


BLOB_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=saalmragdocs;AccountKey=UP7CdMZosnsGy0rAmW0m30yY302uXkvwY4nJDqnGaU9VU0cuXcKbx7UEsDOIC3bLt6330lUWKY2p+AStaTRccA==;EndpointSuffix=core.windows.net"
CONTAINER_NAME="vector-store"

cosmos_service = CosmosService(container_name=CONTAINER_NAME)
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION)

def mock_assistant(chat_id: str, user_msg: str, chat_history: List[str]) -> str:
    
    return postUserResponse(chat_id=chat_id, user_msg=user_msg)

# 参考ドキュメントを作成する
def create_reference_documents(cosmos_items: List[dict]) -> str:

    req_user_msg = user_msg + '\n\n# 検索結果\n'
    
    reference_documents = '◆参考ドキュメント'
    for index, result in enumerate(cosmos_items):
        print('🚀Get content from Azure CosmosDB. : ', result['file_name'], ', ', result['SimilarityScore'])
        
        # システムメッセージにループ番号を追加
        req_user_msg += '## ' + str(index + 1) + '\n' + result['content'] + '\n\n'
        
        # 画面出力する参考ドキュメントに追加
        reference_documents += '\n- ' + result['file_name']
        if result.get('page_number') is not None:
            # page_numberがある場合は追加
            reference_documents += ' (p.' + str(result['page_number']) + ')'
        # 類似度を追加
        reference_documents += ' (類似度: ' + str(result['SimilarityScore']) + ')'
    
    return req_user_msg, reference_documents

# ChatModeを選択するプルダウン。
chat_mode = st.selectbox("ChatModeを選択してください", [chat["display"] for chat in CHAT_MODE])
# チャットModeが選択されたら、CreateChatBotを呼び出す。選択されたモードがすでに選択済みの場合は何もしない
if chat_mode and st.session_state.get("chat_mode") != chat_mode:
    logging.info(f"🚀 st.session_state.get(chat_mode): {st.session_state.get('chat_mode')}")
    logging.info(f"🚀 chat_mode: {chat_mode}")
    instruction = [chat["instructions"] for chat in CHAT_MODE if chat["display"] == chat_mode][0]
    chat_id = createChatBot(instruction=instruction)
    # st.stateにchat_modeとchat_idを保存
    st.session_state.chat_mode = chat_mode
    st.session_state.chat_id = chat_id
    
    # チャットログを初期化
    st.session_state.chat_log = []


# チャットログを保存したセッション情報を初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

user_msg = st.chat_input("メッセージを入力")
if user_msg:
    # 以前のチャットログを表示
    if "chat_log" in st.session_state:
        for chat in st.session_state.chat_log:
            with st.chat_message(chat["name"]):
                st.write(chat["msg"])

    # 最新のユーザメッセージを表示
    with st.chat_message(USER_NAME):
        st.write(user_msg)
    
    # チャットメッセージをベクトル化
    user_msg_embedding = api_embedding(text=user_msg)
    
    # CosmosDBのNoSQLで検索
    cosmos_items = cosmos_service.get_data_by_vector(vector=user_msg_embedding)
    # 検索結果数をログ出力
    logging.info(f"🚀 検索結果数: {len(cosmos_items)}")
    
    # 検索内容を文字列で結合
    req_user_msg, reference_documents = create_reference_documents(cosmos_items)
    logging.info(f"🚀 req_user_msg: {req_user_msg}")

    # アシスタントのメッセージを表示
    res_message = mock_assistant(chat_id=st.session_state.get("chat_id"), user_msg=req_user_msg, chat_history=st.session_state.chat_log)
    res_message += '\n\n' + reference_documents
    logging.info(f"🚀 res_message: {res_message}")
    with st.chat_message(ASSISTANT_NAME):
        assistant_msg = res_message
        assistant_response_area = st.empty()
        assistant_response_area.write(assistant_msg)

    # セッションにチャットログを追加
    st.session_state.chat_log.append({"name": USER_NAME, "msg": user_msg})
    st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": assistant_msg})
    # チャットログを出力
    print(" ■チャットログ:")
    for chat in st.session_state.chat_log:
        print("  " + chat["name"] + ": " + chat["msg"])
    


# サイドバーにチャットログをダウンロードするボタンを追加
# サイトバーを表示
with st.sidebar:
    st.download_button(
        label="Chat DL",
        data=getChatState(chat_id=st.session_state.chat_id),
        file_name="chat_log.json",
        mime="text/plain"
    )