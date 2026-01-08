from pathlib import Path
from messages.repo_agent_message import RepoAgentMessage, RepoAgentResponseMessage
from services.repo2Text import Repo2TextService
from thespian.actors import Actor
from thespian.troupe import troupe
from loguru import logger
from toon import encode

@troupe(max_count=5, idle_count=2)
class RepoAgent(Actor):

    def receiveMessage(self, message, sender):
        if (isinstance(message, RepoAgentMessage)):
            repo_url = message.message
            logger.info("[RepoAgent] received repo_url: {}", repo_url)
            repo_data = Repo2TextService().call_service(repo_url)
            llm_input_data = RepoAgentResponseMessage(encode(repo_data))
            self.send(sender, llm_input_data)
        else:
            self.send(sender, "Unknown command. Please send 'repoAgent' to receive more assistance.")