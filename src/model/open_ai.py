from src.model.model_interface import ModelInterface
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI

class OpenAi(ModelInterface):
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.model_name = "gpt-40"
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = self.initialize_client()
    def initialize_client(self):
        return OpenAI(api_key=self.api_key)
    def generate(self, prompt: str,instruction: str) -> str:
        response =self.client.responses.create(
        model=self.model_name,
        instructions=instruction,
        input=prompt,
        stream=False)   
        return response
    def chat(self, prompt: str, instruction: str) -> str:
        pass