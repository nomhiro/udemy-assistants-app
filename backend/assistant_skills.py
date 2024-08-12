import json
import logging
import azure.functions as func
from openai import AzureOpenAI

from frontend.service.openai_service import openai_service
from task_manager import add_todo_task
from frontend.domain.obj_cosmos_task import CosmosTaskObj
from frontend.service.cosmos_service import cosmos_service

skills = func.Blueprint()

client = AzureOpenAI(
    azure_endpoint="https://aoai-eastus-apimtest-001.openai.azure.com",
    api_key="183101ec494c45aba62b7e1e18365b7f",
    api_version="2024-03-01-preview"
)

@skills.function_name("AddToDoTask")
@skills.assistant_skill_trigger(arg_name="taskDetails", function_description="Create a new todo task")
def add_todo(taskDetails: str) -> None:
    if not taskDetails:
        raise ValueError("Task details cannot be empty")

    logging.info(f"Adding todo: {taskDetails}")
    
    # OpenAIでtaskDetailsからタスク名を取得
    openai_svc = openai_service.AzureOpenAIService(client=client)
    response = openai_svc.getChatCompletion(messages=[{"role": "system", "content": "ユーザメッセージの情報はタスクの詳細情報です。タスク名を生成してください。"}, {"role": "user", "content": taskDetails}], temperature=0.5, top_p=1)
    task_name = response.choices[0].message.content

    task_obj = CosmosTaskObj(task_name=task_name, details=taskDetails, due_date="", priority="medium", status="todo")
    add_todo_task(task_obj)
    return

# すべてのタスクを取得するスキル
@skills.function_name("GetAllTasks")
@skills.assistant_skill_trigger(arg_name="inputIgnored", function_description="タスクを全件取得する")
def get_all_tasks(inputIgnored: str) -> str:
    logging.info("Fetching list of todos")
    
    query = "SELECT c.id, c.task_name, c.details, c.due_date, c.priority, c.status FROM c"
    cosmos_svc = cosmos_service.CosmosService(container_name="tasks")
    
    tasks = cosmos_svc.get_data(query=query)
    
    return json.dumps(tasks)