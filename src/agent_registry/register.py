from src.services.singleton import Singleton
from thespian.actors import Actor

    
class AgentRegistry(metaclass=Singleton):
    def __init__(self):
        self.agents={}
    def register_agent(self,agentName:str,agent:Actor,description:str=""):
        if agentName in self.agents:
            return
        self.agents[agentName] = {
            "agent": agent,
            "description": description
        }
    def get_agents(self):
        return self.agents
    def get_agent(self,agentName:str):
        return self.agents.get(agentName,None)