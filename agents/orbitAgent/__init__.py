from pathlib import Path
from messages.intent_agent_message import IntentAgentMessage
from messages.llm_message import LLMMessage
from model.copilot_model import CopilotModel
from services.file import FileService
from services.repo2Text import Repo2TextService
from thespian.actors import Actor
from model.llama_model import LlamaModel
from model.model_adapter import ModelAdapter
from thespian.troupe import troupe
from loguru import logger
from toon import encode

class OrbitAgent(Actor):

    def __init__(self):
        super().__init__()
        self.model = ModelAdapter(LlamaModel())
        # self.model = ModelAdapter(CopilotModel("gpt-4o"))

    def receiveMessage(self, message, sender):
        if (isinstance(message, IntentAgentMessage)):
            query = message.query
            logger.info("[OrbitAgent] received query: {}", query)
            file_path = Path(__file__).parent
            read_instruction = FileService().read_file(file_path / "orbitAgentInstructions.md")
            repo_url = "https://github.com/R2D2-fwks/orbit"
            repo_data = Repo2TextService().call_service(repo_url)
            llm_input_data = encode(repo_data)
            complete_query = "\nHere are the details of the Orbit repository:\n" + llm_input_data + "\n" + "User Query: "+ query
            response = LLMMessage(self.model.generate(prompt=complete_query, instruction=read_instruction))
            self.send(sender, response)
        else:
            self.send(sender, "Unknown command. Please send 'orbitAgent' to receive more assistance.")