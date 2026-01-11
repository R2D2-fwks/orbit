import json

from pyparsing import Path
from src.agent_registry import register_agents
from src.messages.query import QueryMessage
from src.orchestrator import OrchestratorAgent
from thespian.actors import ActorSystem
from loguru import logger

def start_actor_system(query:str):
    try:
        wrapped_query = QueryMessage(query)
        file_path = Path(__file__).parent.parent.parent/"capabilities.json"
        print(f"Loading capabilities from: {file_path}")
        register_agents()
        with open(file_path, 'r') as f:
            capabilities = json.load(f)
            actor_system = ActorSystem(capabilities=capabilities)
            logger.info("[Start]Starting Agent System...")
            logger.info("[Start]Creating Orchestrator Agent...")
            orchestrator_agent_address = actor_system.createActor(OrchestratorAgent)
            response = actor_system.ask(orchestrator_agent_address, wrapped_query,timeout=50000.0)
            actor_system.shutdown()
            return response
    except Exception as e:
        logger.error(f"Error initializing Actor System: {e}")
    return "Error initializing Actor System."
    

