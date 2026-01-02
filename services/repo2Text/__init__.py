

from services.service_interface import ServiceInterface
from gitingest import ingest
import os
from dotenv import load_dotenv
import asyncio

class Repo2TextService(ServiceInterface):
    def __init__(self):
        load_dotenv()

    def call_service(self, repo_url:str) -> dict:
        # Implement the logic to convert repository data to text
        s,t,c=ingest(repo_url,token=os.getenv("PAT_TOKEN"))
        return {"summary": s, "structure": t, "content": c}