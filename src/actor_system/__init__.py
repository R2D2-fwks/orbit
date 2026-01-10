import json
from src.agent_registry import register_agents
from src.messages.query import QueryMessage
from src.orchestrator import OrchestratorAgent
from thespian.actors import ActorSystem
from loguru import logger

def start_actor_system(query:str):
    wrapped_query = QueryMessage(query)
    with open('capabilities.json', 'r') as f:
        capabilities = json.load(f)
        actor_system = ActorSystem(capabilities=capabilities)
        logger.info("[Start]Starting Agent System...")
        logger.info("[Start]Creating Orchestrator Agent...")
        register_agents()
        orchestrator_agent_address = actor_system.createActor(OrchestratorAgent)
        response = actor_system.ask(orchestrator_agent_address, wrapped_query,timeout=50000.0)
        actor_system.shutdown()
        return response

