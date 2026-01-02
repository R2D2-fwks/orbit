from thespian.actors import Actor
class AgentSingleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
    
class AgentRegistry(metaclass=AgentSingleton):
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