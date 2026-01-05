from pathlib import Path
from agents.orchestrator import messageTypeResolver
from messages.intent_agent_message import IntentAgentMessage
from messages.llm_message import LLMMessage
from model.copilot_model import CopilotModel
from services.read_md_file import read_md_file
from services.repo2Text import Repo2TextService
from thespian.actors import Actor
from model.llama_model import LlamaModel
from model.model_adapter import ModelAdapter
from thespian.troupe import troupe
from loguru import logger

class OrbitAgent(Actor):
    def __init__(self):
        super().__init__()
        self.model = ModelAdapter(LlamaModel())
        # self.model = ModelAdapter(CopilotModel())
    def receiveMessage(self, message, sender):
        if (isinstance(message, IntentAgentMessage)):
            query = message.query
            logger.info("[OrbitAgent] received query: {}", query)
            file_path = Path(__file__).parent
            read_instruction = read_md_file(file_path / "orbitAgentInstructions.md")
            repo_url = "https://github.com/R2D2-fwks/orbit"
            repo_text = Repo2TextService().call_service(repo_url)
            complete_query = read_instruction + "\nHere are the details of the Orbit repository:\n" + f"Repository Summary: {repo_text['summary']}. Structure: {repo_text['structure']}. Content: {repo_text['content']}" + "\n" + query
            response = LLMMessage(self.model.generate(prompt=complete_query, instruction=read_instruction))
            self.send(sender, response)
        else:
            self.send(sender, "Unknown command. Please send 'orbitAgent' to receive more assistance.")