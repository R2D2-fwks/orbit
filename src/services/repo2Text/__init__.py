

from src.services.service_interface import ServiceInterface
from gitingest import ingest,ingest_async
import os
from dotenv import load_dotenv
import gitingest.config
import asyncio
import concurrent.futures

class Repo2TextService(ServiceInterface):
    def __init__(self):
        super().__init__()
        load_dotenv()
        gitingest.config.DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT") or 300)

    def _sync_ingest(self, repo_url: str, max_file_size: int) -> dict:
        """Perform the actual ingest in a sync context."""
        s, t, c = ingest(
            repo_url, 
            token=os.getenv("PAT_TOKEN"), 
            max_file_size=max_file_size
        )
        return {"summary": s, "structure": t, "content": c}
    
    async def call_service_async(self, repo_url: str, options: dict = None) -> dict:
        """Async version for use in async contexts."""
        if options is None:
            options = {}
        MAX_FILE_SIZE = options.get("max_file_size", 5 * 1024 * 1024)
        
        s, t, c = await ingest_async(
            repo_url,
            token=os.getenv("PAT_TOKEN"),
            max_file_size=MAX_FILE_SIZE
        )
        return {"summary": s, "structure": t, "content": c}

    def call_service(self, repo_url:str, options:dict) -> dict:
        if options is None:
            options = {}
        MAX_FILE_SIZE = options.get("max_file_size", 5 * 1024 * 1024)  # Default to 5 MB
        try:
            loop = asyncio.get_running_loop() 
            # We're in an async context, need to use nest_asyncio or run in thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    self._sync_ingest, repo_url, MAX_FILE_SIZE
                )
                return future.result(timeout=300)
        except RuntimeError:
            return self._sync_ingest(repo_url, MAX_FILE_SIZE)
        # Implement the logic to convert repository data to text
        s,t,c=ingest(repo_url,token=os.getenv("PAT_TOKEN"), max_file_size=MAX_FILE_SIZE)
        return {"summary": s, "structure": t, "content": c}