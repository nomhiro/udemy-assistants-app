import streamlit as st
import pandas as pd
import numpy as np
import logging

from openai import AzureOpenAI

from service.openai_service.openai_service import AzureOpenAIService
from service.cosmos_service.cosmos_service import CosmosService
from domain.obj_cosmos_task import CosmosTaskObj
from call_api.call_func_aoai import CreateAssistant, PostUserQuery

logging.basicConfig(level=logging.INFO)

USER_NAME = "user"
ASSISTANT_NAME = "assistant"

CONTAINER_NAME="tasks"

aoai_client = AzureOpenAI(
    # azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    # api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint="https://aoai-eastus-apimtest-001.openai.azure.com",
    api_key="183101ec494c45aba62b7e1e18365b7f",
    api_version="2024-03-01-preview"
)
azure_openai_service = AzureOpenAIService(client=aoai_client)
cosmos_service = CosmosService(container_name=CONTAINER_NAME)

def mock_assistant(user_msg: str, chat_history) -> str:
  return "Hello! How can I help you today?"

def display_tasks():
  # CosmosDBからステータスがDoneではないタスクを取得
  query = "SELECT c.id, c.task_name, c.details, c.priority, c.status FROM c"
  cosmos_items = cosmos_service.get_data(query=query)
  logging.info(f"🚀 検索結果数: {len(cosmos_items)}")
  
  # タスク一覧(cosmos_items)をGridで表示
  st.write("■タスク一覧")
  # ステータスがdone以外のタスクを抽出
  not_done_tasks = [task for task in cosmos_items if task["status"] != "done"]
  # id列を無くす
  for task in not_done_tasks:
    task.pop("id", None)
  df = pd.DataFrame(not_done_tasks)
  st.table(df)
  
  return cosmos_items

# ブラウザのタブのタイトルを設定
st.set_page_config(page_title="ToDo App", page_icon=":clipboard:", layout="wide")

# タスク一覧の表示領域を作成
task_display_area = st.empty()
  
with st.expander("タスク登録"):
  with st.form(key='task_form'):
    task_name = st.text_input("タスク名")
    task_detail = st.text_area("タスク詳細")
    task_priority = st.selectbox("優先度", ["high", "medium", "low"])
    task_due = st.date_input("期日")
    submit_button = st.form_submit_button("登録")

    if submit_button:
      logging.info(f"🚀新しいタスク: {task_name}")
      logging.info(f"🚀タスクの詳細: {task_detail}")
      logging.info(f"🚀優先度: {task_priority}")
      logging.info(f"🚀期日: {task_due}")
      # タスクを新規登録する処理を実装する
      # due_dateをYYYY-MM-DD形式の文字列に変換
      formatted_due_date = task_due.strftime('%Y-%m-%d')
      obj_task = CosmosTaskObj(task_name=task_name, details=task_detail, due_date=formatted_due_date, priority=task_priority, status="todo")
      cosmos_service.insert_data(obj_task.to_dict())

# タスク一覧を表示する関数を更新領域内で呼び出す
with task_display_area:
    cosmos_items = display_tasks()
  
# with col2:
with st.sidebar:
  st.write("■チャット画面")
  # チャットログを保存したセッション情報を初期化
  if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

  instruction = f"""あなたはタスクを管理しているアシスタントです。"過去のタスク"を参考にして、ユーザからの問い合わせに応答してください。
  
  ## 過去のタスク
  {cosmos_items}"""
  logging.info(f"🚀 instruction: {instruction}")
  assistantId = CreateAssistant(instruction=instruction)
  # st.stateにassistantIdを保存
  st.session_state.assistantId = assistantId

  # チャットログを表示するコンテナ
  chat_log_container = st.container()

  # 以前のチャットログを表示
  for chat in st.session_state.chat_log:
    with chat_log_container:
      with st.chat_message(chat["name"]):
        st.write(chat["msg"])

  # チャット入力部品を画面の一番下に表示するためのコンテナ
  with st.container():
    user_msg = st.chat_input("メッセージを入力")
    if user_msg:
      # 最新のユーザメッセージを表示
      with st.chat_message(USER_NAME):
        st.write(user_msg)

      # アシスタントのメッセージを取得して表示
      res_message = PostUserQuery(assistantId=assistantId, user_msg=user_msg)
      with st.chat_message(ASSISTANT_NAME):
        assistant_msg = res_message
        assistant_response_area = st.empty()
        assistant_response_area.write(assistant_msg)

      # セッションにチャットログを追加
      st.session_state.chat_log.append({"name": USER_NAME, "msg": user_msg})
      st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": assistant_msg})
      
      # チャット入力後、タスク一覧を更新
      with task_display_area:
        cosmos_items = display_tasks()
      