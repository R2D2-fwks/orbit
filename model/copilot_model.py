from ghcopilot import GithubCopilotClient as GhCopilotClient
from dotenv import load_dotenv
from model.model_interface import ModelInterface
from loguru import logger


class CopilotModel(ModelInterface):
    def __init__(self, model_id: str = None):
        super().__init__()
        load_dotenv()
        self.client = self.initialize_client()
        self.model_id = model_id
    def initialize_client(self):
        client =GhCopilotClient()
        if not client.load_token_from_file():
            cookies = client.get_cookies()
            client.authenticate(cookies)
            client.save_token_to_file()
        logger.info("[CopilotModel] Authentication successful!")
        return client
    
    def get_model(self) -> str:
        models = self.client.get_models()
        logger.info(f"[CopilotModel] Available models: {models}")
        if self.model_id is not None:
            model_id = self.model_id
        else:
            model_id = models[0]["id"]
        logger.info(f"[CopilotModel] Using model: {model_id}")
        return model_id
    
    def create_thread(self):
        thread_id = self.client.create_new_thread()
        logger.info(f"[CopilotModel] Created new thread with ID: {thread_id}")
        return thread_id

    def generate(self, prompt: str,instruction: str) -> str:
        try:
            complete_prompt = instruction + " " + prompt
            model_id = self.get_model()
            thread_id = self.create_thread()
            response = ""
            for message in self.client.send_message(complete_prompt, model_id=model_id, thread_id=thread_id):
                if message["type"] == "content":
                    response += message["text"]
                else:
                    logger.debug(f"[CopilotModel] Received non-content message: {message}")
            if response.strip() == "":
                logger.warning("[CopilotModel] Received empty response from model.")
                return "No response generated."
            return response
        except Exception as e:
            logger.error(f"[CopilotModel] Error generating response: {e}")
            return "Error generating response."