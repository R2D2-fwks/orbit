from model.model_interface import ModelInterface
import requests
import json
class LlamaModel(ModelInterface):

    def __init__(self,model_name: str = "llama3",model_url: str = "http://127.0.0.1:11434"):
        super().__init__()
        self.model_name = model_name
        self.model_url = model_url
        self.prev_chunk=[]
        self.headers = {'Content-Type': 'application/json'}
        
    def generate(self, prompt: str, instruction: str) -> str:
        # Generate a response using the LLaMA model
        payload = {
            "model": self.model_name,
            "prompt":instruction + " " + prompt,
            "stream": False,
            "think":False,
            # "system":instruction
            
        }
        url = f"{self.model_url}/api/generate"
        response = requests.post(url, 
        headers=self.headers, 
        json=payload,
        timeout=60)
        response_json= json.loads(response.text)
        return response_json["response"]
    
    def chat(self, prompt: str, instruction: str) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "think":False,
            "messages":self.prev_chunk,
            "system":instruction
        }
        url = f"{self.model_url}/api/chat"
        response = requests.post(url, 
        headers=self.headers, 
        json=payload,
        timeout=60)
        response_json= json.loads(response.text)
        self.prev_chunk.append({"role":"user","content":prompt})
        print(f"[LlamaModel] Chat response: {response_json}")
        return response_json["message"]["content"]