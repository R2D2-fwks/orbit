from model.model_interface import ModelInterface
import requests
import os
from dotenv import load_dotenv
from anthropic import Anthropic

class Claude(ModelInterface):
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.model_name = "claude-sonnet-4-5"
        self.api_key = os.getenv("CLAUDE_API_KEY")
        self.client = self.initialize_client()
    def initialize_client(self):
        return Anthropic(api_key=self.api_key)
    def generate(self, prompt: str,instruction: str) -> str:
        response =self.client.messages.create(
        model=self.model_name,
        messages=[{"role": "user", "content": instruction+" "+prompt}],
        input=prompt,
        max_tokens=5000,
        stream=False)   
        return response
    def chat(self, prompt: str, instruction: str) -> str:
        pass