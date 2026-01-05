from model.model_interface import ModelInterface
import requests
import json
class LlamaModel(ModelInterface):
    def __init__(self,model_name: str = "llama3",model_url: str = "http://127.0.0.1:11434"):
        super().__init__()
        self.model_name = model_name
        self.model_url = model_url
        self.headers = {'Content-Type': 'application/json'}
    def generate(self, prompt: str, instruction: str) -> str:
        # Generate a response using the LLaMA model
        payload = {
            "model": self.model_name,
            "prompt": instruction+" "+prompt,
            "stream": False
        }
        url = f"{self.model_url}/api/generate"
        response = requests.post(url, 
        headers=self.headers, 
        json=payload,
        timeout=60)
        response_json= json.loads(response.text)
        return response_json["response"]