import logging
import os
from openai import AzureOpenAI
 
class AzureOpenAIService:
    def __init__(self) -> None:
        # Azure OpenAIのクライアント作成
        self.client = AzureOpenAI(
            azure_endpoint="https://aoai-eastus-apimtest-001.openai.azure.com",
            api_key="183101ec494c45aba62b7e1e18365b7f",
            api_version="2024-03-01-preview"
        )
    
    # AzureOpenAI clientを引数指定する
    def __init__(self, client: AzureOpenAI) -> None:
        self.client = client

    def getChatCompletion(self, messages, temperature, top_p):
        try:
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=float(temperature),
                top_p=float(top_p)
            )

            return response
        except Exception as e:
            logging.error(f'🚀❌Error at getChatCompletion: {e}')
            raise e
    
    def getChatCompletionJsonMode(self, messages, temperature, top_p):
        try:
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                response_format={ "type": "json_object" },
                temperature=float(temperature),
                top_p=float(top_p)
            )

            return response
        except Exception as e:
            logging.error(f'🚀❌Error at getChatCompletion: {e}')
            raise e
    
    def getEmbedding(self, input):
        try:
            response = self.client.embeddings.create(
                input=input,
                model="text-embedding-3-large"
            )
            return response.data[0].embedding
        except Exception as e:
            logging.error(f'🚀❌Error at getEmbedding: {e}')
            raise e