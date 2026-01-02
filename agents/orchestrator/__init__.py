from agents.orchestrator import messageTypeResolver
from thespian.actors import Actor
from thespian.troupe import troupe
from loguru import logger
from colorama import Fore

@troupe(max_count=10, idle_count=3)
class OrchestratorAgent(Actor):
    def __init__(self):
        super().__init__()
    def receiveMessage(self, message, sender):
        logger.info("[Orchestrator] Sender Address: {}", sender)
        orchestrator= self
        context=(message,orchestrator)
        response= messageTypeResolver.checkMessage(context)
        print(f"{Fore.BLUE}\nLLM Responsed: {response}\n")

        