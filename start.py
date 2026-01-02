
from urllib import response
from agents.agentRegistry import AgentRegistry
from agents.orbitAgent import OrbitAgent
from agents.orchestrator import OrchestratorAgent
from agents.troubleshootingAgent import TroubleshootingAgent
from messages.query import QueryMessage
from thespian.actors import ActorSystem
import json
from loguru import logger
import click
from colorama import Fore
from art import text2art


if __name__ == "__main__":
    Art = text2art("ORBIT !", font='big')
    print(Art)
    with open('capabilities.json', 'r') as f:
        capabilities = json.load(f)
        artl1 = text2art("Welcome...", font='small',)
        artl2 = text2art("To ORBIT", font='small')
        print(f"{Fore.BLUE}{artl1}")
        print(f"{Fore.BLUE}{artl2}")
        click.pause()
        click.clear()
        artl4 = text2art("Question?", font='bubble')
        print(f"{Fore.RED}{artl4}")
        query = click.prompt('What is your Query?', type=str, default='How can I use ORBIT framework ?', show_default=True, err=False, prompt_suffix='\n>> ')
        print(f"{Fore.GREEN}\nGreat! You asked: {query}\n")
        print(f"{Fore.YELLOW}Processing your query, please wait...\n")
        wrapped_query = QueryMessage(query)
        system = ActorSystem(capabilities=capabilities)
        logger.info("[Start]Starting Agent System...")
        logger.info("[Start]Creating Orchestrator Agent...")
        orchestrator_agent_address = system.createActor(OrchestratorAgent)
        logger.info("[ActorSystem]Orchestrator Agent Created at address: {}", orchestrator_agent_address)
        logger.info("[Start]Registering Agents in Agent Registry...")
        agent_registry=AgentRegistry()
        agent_registry.register_agent("TroubleshootingAgent", TroubleshootingAgent,description="Agent specialized in troubleshooting technical issues.")
        agent_registry.register_agent("OrbitAgent", OrbitAgent,description="Agent specialized in handling framework related queries and tasks. Any questions related to framework/toolkit on how to use it.")
        system.ask(orchestrator_agent_address, wrapped_query)