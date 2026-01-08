from services.singleton import SingletonClass
from thespian.actors import Actor
    
class AgentRegistry(metaclass=SingletonClass):
    def __init__(self):
        self.agents={}
    def register_agent(self,agentName:str,agent:Actor,description:str=""):
        self.agents[agentName] = {
            "agent": agent,
            "description": description
        }
    def get_agents(self):
        return self.agents
    def get_agent(self,agentName:str):
        return self.agents.get(agentName,None)