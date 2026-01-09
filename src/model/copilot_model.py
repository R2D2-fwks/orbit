from pathlib import Path
from ghcopilot import GithubCopilotClient as GhCopilotClient
from dotenv import load_dotenv
from src.model.model_interface import ModelInterface
from loguru import logger


class CopilotModel(ModelInterface):
    def __init__(self, model_id: str = None):
        super().__init__()
        load_dotenv()
        self.client = self.__initialize_client()
        self.model_id = model_id
        self.thread_id = None

    def __initialize_client(self):
        file_path = Path(__file__).parent.parent.parent / "temp/copilot_token.txt"
        client =GhCopilotClient()
        if not client.load_token_from_file(file_path):
            cookies = client.get_cookies()
            client.authenticate(cookies)
            client.save_token_to_file(file_path)
        logger.info("[CopilotModel] Authentication successful!")
        return client
    
    def __get_model(self) -> str:
        models = self.client.get_models()
        logger.info(f"[CopilotModel] Available models: {models}")
        if self.model_id is not None:
            model_id = self.model_id
        else:
            model_id = models[0]["id"]
        logger.info(f"[CopilotModel] Using model: {model_id}")
        return model_id
    
    def __create_thread(self):
        self.thread_id = self.client.create_new_thread()
        logger.info(f"[CopilotModel] Created new thread with ID: {self.thread_id}")
        return self.thread_id
    
    def __get_latest_thread(self)-> str:
        self.thread_id = self.client.get_latest_thread()
        logger.info(f"[CopilotModel] Using existing thread with ID: {self.thread_id}")
        return self.thread_id
    
    def __delete_thread(self, thread_id: str) -> bool:
        try:
            success = self.client.delete_thread(thread_id)
            self.thread_id = None
            if success:
                logger.info(f"[CopilotModel] Deleted thread with ID: {thread_id}")
            else:
                logger.warning(f"[CopilotModel] Failed to delete thread with ID: {thread_id}")
            return success
        except Exception as e:
            logger.error(f"[CopilotModel] Error deleting thread {thread_id}: {e}")
            return False

    def generate(self, prompt: str,instruction: str) -> str:
        thread_id = self.__create_thread()
        response = self.__send_message(prompt, instruction, thread_id)
        self.__delete_thread(thread_id)
        return response
        
    def chat(self, prompt: str, instruction: str) -> str:
        self.thread_id = self.__get_latest_thread()
        if not self.thread_id:
            self.thread_id = self.__create_thread()
        response = self.__send_message(prompt, instruction, self.thread_id)
        return response
        
    def __send_message(self, prompt: str, instruction: str, thread_id: str=None) -> str:
        try:
            model_id = self.__get_model()
            complete_prompt = instruction + " " + prompt
            response = ""
            for message in self.client.send_message(complete_prompt, model_id=model_id, thread_id=thread_id):
                if message["type"] == "content":
                    response += message["text"]
                else:
                    logger.debug(f"[CopilotModel] Received non-content message: {message}")
            if response.strip() == "":
                logger.warning("[CopilotModel] Received empty response from model.")
                return None
            return response
        except Exception as e:
            logger.error(f"[CopilotModel] Error generating response: {e}")
            return None