from datetime import timedelta
from pathlib import Path
from services.file.read_json_file import read_json_file
from services.repo2Text import Repo2TextService
from services.text2Embeddings import docs_to_vector
from thespian.actors import Actor,WakeupMessage
from vector_db.db_adapter import DatabaseAdapter
from vector_db.milvus.db import MilvusDatabase

class RepoIngestionAgent(Actor):
    def __init__(self):
        super().__init__()
        self.db = DatabaseAdapter(MilvusDatabase())
        self.agent_name = "RepoIngestionAgent"
        
    def receiveMessage(self, message, sender):
        if isinstance(message, str) and message == "start":
            # Start the scheduling loop
            self._schedule_next_wakeup()
            self.send(sender, "Scheduler started")
        
        elif isinstance(message, WakeupMessage):
            # This is triggered every 2 hours
            self._do_scheduled_work()
            # Re-schedule for the next 2-hour interval
            self._schedule_next_wakeup()

    def _schedule_next_wakeup(self):
        # Schedule wakeup in 2 hours
        self.wakeupAfter(timedelta(hours=2))
    
    def _do_scheduled_work(self):
        # Your periodic task logic here
        file_path = Path(__file__).parent
        repo_details = read_json_file(file_path / "repo_details.json")
        repo_data=[]
        for repo_url in repo_details.get("repos", []):
            repo_res = Repo2TextService().call_service(repo_url)
            repo_text=""
            for repo_key in repo_res.keys():
                repo_text+=f"{repo_key.capitalize()}: {repo_res[repo_key]}. "
            repo_data.append(repo_text)
        vectors = docs_to_vector(repo_data,"repo_details")
        self.db.insert_vectors(vectors)