
from src.agent_registry.register import AgentRegistry
from src.agents.orbitAgent import OrbitAgent
from src.agents.troubleshootingAgent import TroubleshootingAgent


def register_agents():
    agent_registry=AgentRegistry()

    agent_registry.register_agent("TroubleshootingAgent", TroubleshootingAgent,description="""Agent 
                                  specialized in troubleshooting technical issues.""")
    agent_registry.register_agent("OrbitAgent", OrbitAgent,description="""Agent 
                                  specialized in handling framework related queries 
                                  and tasks. 
                                  Any questions related to framework/toolkit on how 
                                  to use it.""")