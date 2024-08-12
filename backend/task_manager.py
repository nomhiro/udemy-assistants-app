import abc
import logging
import os

from frontend.domain.obj_cosmos_task import CosmosTaskObj
from frontend.service.cosmos_service.cosmos_service import CosmosService

CONTAINER_NAME="tasks"

cosmos_service = CosmosService(container_name=CONTAINER_NAME)

def add_todo_task(task_obj: CosmosTaskObj):
  logging.info(f"🚀新しいタスク: {task_obj.to_dict()}")
  # タスクを新規登録する処理を実装する
  # due_dateをYYYY-MM-DD形式の文字列に変換
  cosmos_service.insert_data(task_obj.to_dict())