
from src.messages.query import QueryMessage
from src.orchestrator import messageTypeResolver
from thespian.actors import Actor
from thespian.troupe import troupe
from loguru import logger
from colorama import Fore

@troupe(max_count=10, idle_count=3)
class OrchestratorAgent(Actor):
    def __init__(self):
        super().__init__()
        self.original_sender = None
    def receiveMessage(self, message, sender):
        logger.info("[Orchestrator] Sender Address: {}", sender)
        orchestrator= self
        context=(message,orchestrator,sender)
        if(isinstance(message,QueryMessage)):
            self.original_sender= sender
        response= messageTypeResolver.checkMessage(context)
        if(isinstance(response,str)):
            self.send(self.original_sender, response)

        