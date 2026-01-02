from pathlib import Path
from agents.orchestrator import messageTypeResolver
from messages.intent_agent_message import IntentAgentMessage
from messages.llm_message import LLMMessage
from services.read_md_file import read_md_file
from thespian.actors import Actor
from model.llama_model import LlamaModel
from model.model_adapter import ModelAdapter
from thespian.troupe import troupe
from loguru import logger

class OrbitAgent(Actor):
    def __init__(self):
        super().__init__()
        self.model = ModelAdapter(LlamaModel())
    def receiveMessage(self, message, sender):
        if (isinstance(message, IntentAgentMessage)):
            query = message.query
            logger.info("[OrbitAgent] received query: {}", query)
            file_path = Path(__file__).parent
            read_instruction = read_md_file(file_path / "orbitAgentInstructions.md")
            complete_message =  read_instruction+" "+query
            response = LLMMessage(self.model.generate(complete_message))
            self.send(sender, response)
        else:
            self.send(sender, "Unknown command. Please send 'orbitAgent' to receive more assistance.")