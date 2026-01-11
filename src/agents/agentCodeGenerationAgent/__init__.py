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

class AgentCodeGenerationAgent(Actor):

    def __init__(self):
        super().__init__()
        self.model = ModelAdapter(LlamaModel())
        # self.model = ModelAdapter(CopilotModel("gpt-4o"))

    def receiveMessage(self, message, sender):
        if (isinstance(message, IntentAgentMessage)):
            query = message.query
            logger.info("[AgentCodeGenerationAgent] received query: {}", query)
           
            self.send(sender, response)
        else:
            self.send(sender, "Unknown command. Please send 'orbitAgent' to receive more assistance.")