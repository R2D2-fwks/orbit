from asyncio.log import logger
from pathlib import Path
from pyexpat import model
from messages.intent_agent_message import IntentAgentMessage
from messages.llm_message import LLMMessage
from model.copilot_model import CopilotModel
from services.file.read_json_file import read_json_file
from services.file.read_md_file import read_md_file
from services.repo2Text import Repo2TextService
from services.text2Embeddings import docs_to_vector, text_to_vector
from thespian.actors import Actor
from model.llama_model import LlamaModel
from model.model_adapter import ModelAdapter
from vector_db.db_adapter import DatabaseAdapter
from vector_db.milvus.db import MilvusDatabase
from toon import encode
class TroubleshootingAgent(Actor):
    def __init__(self):
        super().__init__()
        self.model = ModelAdapter(LlamaModel())
        self.db = DatabaseAdapter(MilvusDatabase())
        # self.model = ModelAdapter(CopilotModel("gpt-4o"))
        self.agent_name = "TroubleshootingAgent"
    def receiveMessage(self, message, sender):
        if (isinstance(message, IntentAgentMessage)):
            query = message.query
            file_path = Path(__file__).parent
            read_instruction = read_md_file(file_path / "troubleshootingGuidelines.md")
            query_vector = text_to_vector(query)
            search_results = self.db.search_vectors(query_vector, top_k=5,filter="tags == 'repo_details'")
            search_result_toon = encode(search_results)
            complete_query =   " \nHere are the details of the repositories in toon format:\n " + search_result_toon + "\n User Query: " + query
            logger.info("[TroubleshootingAgent] prepare to generate response with complete_query")
            # repo_texts = " ".join([f"Repository Summary: {repo['summary']}. Structure: {repo['structure']}. Content: {repo['content']}" for repo in repo_texts])
            # complete_query =   " \nHere are the details of the repositories:\n " + repo_texts + "\n User Query: " + query
            # logger.info("[TroubleshootingAgent] prepare to generate response with complete_query")
            response = LLMMessage(self.model.generate(complete_query, read_instruction))
            self.send(sender, response)
        else:
            self.send(sender, "Unknown command. Please send 'troubleshoot' to receive troubleshooting assistance.")