

from services.service_interface import ServiceInterface
from gitingest import ingest
import os
from dotenv import load_dotenv
import gitingest.config

class Repo2TextService(ServiceInterface):
    def __init__(self):
        super().__init__()
        load_dotenv()
        gitingest.config.DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT") or 300)

    def call_service(self, repo_url:str, options:dict) -> dict:
        MAX_FILE_SIZE = options.get("max_file_size", 5 * 1024 * 1024)  # Default to 5 MB
        # Implement the logic to convert repository data to text
        s,t,c=ingest(repo_url,token=os.getenv("PAT_TOKEN"), max_file_size=MAX_FILE_SIZE)
        return {"summary": s, "structure": t, "content": c}