from agents.orchestrator import messageTypeResolver
from agents.repoIngestionAgent import RepoIngestionAgent
from messages.query import QueryMessage
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
        repo_agent = self.createActor(RepoIngestionAgent)
        self.send(repo_agent, "start")
        context=(message,orchestrator,sender)
        if(isinstance(message,QueryMessage)):
            self.original_sender= sender
        response= messageTypeResolver.checkMessage(context)
        if(isinstance(response,str)):
            self.send(self.original_sender, response)

        