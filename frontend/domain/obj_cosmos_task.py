import uuid

class CosmosTaskObj:
    def __init__(self, 
                 task_name: str, 
                 details: str, 
                 due_date: str,  # YYYY-MM-DD形式の文字列で期日を扱う
                 priority: int,  # 数値で優先度を扱う（例：1=高, 2=中, 3=低）
                 status: str):  # 文字列でステータスを扱う（例：'未完了', '完了'）
        self.id = str(uuid.uuid4())
        self.task_name = task_name
        self.details = details
        self.due_date = due_date
        self.priority = priority
        self.status = status
    
    def to_dict(self):
        return {
            "id": self.id,
            "task_name": self.task_name,
            "details": self.details,
            "due_date": self.due_date,
            "priority": self.priority,
            "status": self.status
        }
    
    @staticmethod
    def from_dict(dict):
        return CosmosTaskObj(dict["task_name"],
                             dict["details"], 
                             dict["due_date"], 
                             dict["priority"],
                             dict["status"])
    
    def __str__(self):
        return f'id: {self.id}, task_name: {self.task_name}, details: {self.details}, due_date: {self.due_date}, priority: {self.priority}, status: {self.status}'