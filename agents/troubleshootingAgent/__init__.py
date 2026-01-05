from asyncio.log import logger
from pathlib import Path
from pyexpat import model
from messages.intent_agent_message import IntentAgentMessage
from messages.llm_message import LLMMessage
from model.copilot_model import CopilotModel
from services.read_json_file import read_json_file
from services.read_md_file import read_md_file
from services.repo2Text import Repo2TextService
from thespian.actors import Actor
from model.llama_model import LlamaModel
from model.model_adapter import ModelAdapter

class TroubleshootingAgent(Actor):
    def __init__(self):
        super().__init__()
        self.model = ModelAdapter(LlamaModel())
        # self.model = ModelAdapter(CopilotModel("gpt-4o"))
        self.agent_name = "TroubleshootingAgent"
    def receiveMessage(self, message, sender):
        if (isinstance(message, IntentAgentMessage)):
            query = message.query
            file_path = Path(__file__).parent
            read_instruction = read_md_file(file_path / "troubleshootingGuidelines.md")
            repo_details = read_json_file(file_path / "repo_details.json")
            repo_texts = []
            for repo_url in repo_details.get("repos", []):
                repo_text = Repo2TextService().call_service(repo_url)
                repo_texts.append(repo_text)
            repo_texts = " ".join([f"Repository Summary: {repo['summary']}. Structure: {repo['structure']}. Content: {repo['content']}" for repo in repo_texts])
            complete_query =   " \nHere are the details of the repositories:\n " + repo_texts + "\n User Query: " + query
            logger.info("[TroubleshootingAgent] prepare to generate response with complete_query")
            response = LLMMessage(self.model.generate(complete_query, read_instruction))
            self.send(sender, response)
        else:
            self.send(sender, "Unknown command. Please send 'troubleshoot' to receive troubleshooting assistance.")