from ghcopilot import GithubCopilotClient as GhCopilotClient
import os
from dotenv import load_dotenv
from model.model_interface import ModelInterface
from loguru import logger
from colorama import Fore


class CopilotModel(ModelInterface):
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.client = self.initialize_client()
        self.model_id = "gpt-4o-2024-08-06"
    def initialize_client(self):
        client =GhCopilotClient()
        if not client.load_token_from_file():
            cookies = client.get_cookies()
            client.authenticate(cookies)
            client.save_token_to_file()
        logger.info("[Copilot] Authentication successful!")
        return client
    def get_model(self) -> str:
        models = self.client.get_models()
        logger.info(f"[Copilot] Available models: {models}")
        if self.model_id is not None:
            model_id = self.model_id
        else:
            model_id = models[0]["id"]
        logger.info(f"[Copilot] Using model: {model_id}")
        return model_id
    def create_thread(self):
        thread_id = self.client.create_new_thread()
        logger.info(f"[Copilot] Created new thread with ID: {thread_id}")
        return thread_id

    def generate(self, prompt: str,instruction: str) -> str:
        complete_prompt = instruction + " " + prompt
        model_id = self.get_model()
        thread_id = self.create_thread()
        response = ""
        for message in self.client.send_message(complete_prompt, model_id=model_id, thread_id=thread_id):
            if message["type"] == "content":
                response += message["text"]
        logger.info("[Copilot] Generated response successfully.")
        return response