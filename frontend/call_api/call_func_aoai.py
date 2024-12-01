import datetime
import logging
import requests
import random

# バックエンド側のFunctionsAPI群を呼び出す

URL = "http://localhost:7071/"

# CreateChatBotを呼び出す
# RESTのPUTメソッド
# INPUT
# chatID(str)を日時+ラインダムな4文字で生成する
def createChatBot(instruction: str):
  try: 
    logging.info(f"🚀 instruction: {instruction}")
    
    chat_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "-" + str(random.randint(1000, 9999))
    
    # URL/chats/{chatID}でPUTメソッドを呼び出す。
    # リクエストパラメータにinstructionを設定
    response = requests.put(URL + f"api/chats/{chat_id}", json={"instructions": instruction})
    res_json = response.json()
    logging.info(f"🚀 chat_id: {res_json['chatId']}")
  
    return res_json['chatId']
  
  except Exception as e:
    logging.error(f"🚀 Error: {e}")
    raise e

def postUserResponse(chat_id: str, user_msg: str):
  try: 
    # URL/chats/{chatID}でPOSTメソッドを呼び出す
    # リクエストパラメータにuser_messageを設定
    req_url = URL + f"api/chats/{chat_id}"
    logging.info(f"🚀 req_url: {req_url}")
    response = requests.post(req_url, params={"message": user_msg})
    logging.info(f"🚀 response.text: {response.text}")
    
    return response.text
  
  except Exception as e:
    logging.error(f"🚀 Error: {e}")
    raise e

# チャット履歴を取得
def getChatState(chat_id: str):
  try:
    # URL/chats/{chatID}でGETメソッドを呼び出す
    response = requests.get(URL + f"api/chats/{chat_id}", params={"timestampUTC": "2024-06-01T07:51:10Z"})
    logging.info(f"🚀 response.text: {response.text}")
    
    return response.text
  
  except Exception as e:
    logging.error(f"🚀 Error: {e}")
    raise e

def api_embedding(text: str):
    
    url = f"{URL}/api/embeddings"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "RawText": text,
        "FilePath": None
    }
    response = requests.post(url, headers=headers, json=data)
    embedding = response.json().get("response").get("data")[0].get("embedding")

    return embedding


# Assistant
# CreateAssistantを呼び出す
# RESTのPUTメソッド
# INPUT
# assistantId(str)を日時+ラインダムな4文字で生成する
def CreateAssistant(instruction: str):
  try: 
    logging.info(f"🚀 instruction: {instruction}")
    
    assistantId = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "-" + str(random.randint(1000, 9999))
    
    # URL/chats/{chatID}でPUTメソッドを呼び出す。
    # リクエストパラメータにinstructionを設定
    response = requests.put(URL + f"api/assistants/{assistantId}", json={"instructions": instruction})
    res_json = response.json()
    logging.info(f"🚀 assistantId: {res_json['assistantId']}")
  
    return res_json['assistantId']
  
  except Exception as e:
    logging.error(f"🚀 Error: {e}")
    raise e

def PostUserQuery(assistantId: str, user_msg: str):
  try: 
    # URL/chats/{chatID}でPOSTメソッドを呼び出す
    # リクエストパラメータにuser_messageを設定
    req_url = URL + f"api/assistants/{assistantId}"
    logging.info(f"🚀 req_url: {req_url}")
    response = requests.post(req_url, params={"message": user_msg})
    logging.info(f"🚀 response.text: {response.text}")
    
    return response.text
  
  except Exception as e:
    logging.error(f"🚀 Error: {e}")
    raise e