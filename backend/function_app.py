import json
import logging
import azure.functions as func

from assistant_api import apis
from assistant_skills import skills


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
# skills = func.Blueprint()

# チャット
# @app.function_name("CreateChatBot")
# @app.route(route="chats/{chatID}", methods=["PUT"])
# @app.assistant_create_output(arg_name="requests")
# def create_chat_bot(req: func.HttpRequest, requests: func.Out[str]) -> func.HttpResponse:
#     # リクエストパラメータからchatIDを取得
#     chatID = req.route_params.get("chatID")
#     input_json = req.get_json()
#     logging.info(f"Creating chat ${chatID} from input parameters ${json.dumps(input_json)}")
#     # リクエストパラメータを設定
#     create_request = {
#         "id": chatID,
#         "instructions": input_json.get("instructions")
#     }
#     requests.set(json.dumps(create_request))
#     response_json = {"chatId": chatID}
#     return func.HttpResponse(json.dumps(response_json), status_code=202, mimetype="application/json")


# @app.function_name("GetChatState")
# @app.route(route="chats/{chatID}", methods=["GET"])
# @app.assistant_query_input(arg_name="state", id="{chatID}", timestamp_utc="{Query.timestampUTC}")
# def get_chat_state(req: func.HttpRequest, state: str) -> func.HttpResponse:
#     return func.HttpResponse(state, status_code=200, mimetype="application/json")


# @app.function_name("PostUserResponse")
# @app.route(route="chats/{chatID}", methods=["POST"])
# @app.assistant_post_input(arg_name="state", id="{chatID}", user_message="{Query.message}", model="%CHAT_MODEL_DEPLOYMENT_NAME%")
# def post_user_response(req: func.HttpRequest, state: str) -> func.HttpResponse:
#     # stateから最新のメッセージを取得
#     data = json.loads(state)
#     recent_message_content = data['recentMessages'][0]['content']
#     return func.HttpResponse(recent_message_content, status_code=200, mimetype="text/plain")

# @app.function_name("GenerateEmbeddings")
# @app.route(route="embeddings", methods=["POST"])
# @app.embeddings_input(arg_name="embeddings", input="{rawText}", input_type="rawText", model="%EMBEDDING_MODEL_DEPLOYMENT_NAME%")
# def generate_embeddings_http_request(req: func.HttpRequest, embeddings: str) -> func.HttpResponse:
#     user_message = req.get_json()
#     embeddings_json = json.loads(embeddings)
#     embeddings_request = {
#         "raw_text": user_message.get("RawText"),
#         "file_path": user_message.get("FilePath")
#     }
#     logging.info(f'Received {embeddings_json.get("count")} embedding(s) for input text '
#         f'containing {len(embeddings_request.get("raw_text"))} characters.')
    
#     return func.HttpResponse(json.dumps(embeddings_json), status_code=200, mimetype="application/json")




app.register_functions(apis)
app.register_functions(skills)



# @skills.function_name("GetTodos")
# @skills.assistant_skill_trigger(arg_name="inputIgnored", function_description="Fetch the list of previously created todo tasks")
# def get_todos(inputIgnored: str) -> str:
#     logging.info("Fetching list of todos")
#     results = todo_manager.get_todos()
#     return json.dumps(results)
    