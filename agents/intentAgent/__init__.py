import json
from agents.agentRegistry import AgentRegistry
from messages.intent_agent_message import IntentAgentMessage
from messages.query import QueryMessage
from model.copilot_model import CopilotModel
from services.file import FileService
from thespian.actors import Actor
from model.llama_model import LlamaModel
from model.model_adapter import ModelAdapter
from pathlib import Path
from loguru import logger
class IntentAgent(Actor):
    def __init__(self):
        super().__init__()
        # self.model = ModelAdapter(LlamaModel())
        self.model = ModelAdapter(CopilotModel())
        self.agent_name = "IntentAgent"
    def receiveMessage(self, msg, sender):
        if isinstance(msg, QueryMessage):
            message = msg.message
            agent_registry=AgentRegistry()
            agents = agent_registry.get_agents()
            agent_info ={}
            agent_names = agents.keys()
            for agent_name in agent_names:
                agent_info[agent_name] = agents[agent_name]["description"]
            agent_names_description_string = json.dumps(agent_info)
            logger.info("[IntentAgent] agent_names_description_string: {}", agent_names_description_string)
            file_path = Path(__file__).parent
            agent_instructions = FileService().read_file(file_path / "intentAgentGuidelines.md")
            complete_message = "Agent Names and descriptions: " +agent_names_description_string  +" Query from User: " + message
            llm_response = self.model.generate(prompt=complete_message, instruction=agent_instructions)
            logger.info("[IntentAgent] llm_response: {}", llm_response)
            intent_response = IntentAgentMessage(self.parse_response(llm_response),message)
            logger.info("[IntentAgent] intent_response: {}", intent_response)
            self.send(sender, intent_response)
        else:
            self.send(sender, "Unknown command. Please send a QueryMessage to identify intent.")

    def parse_response(self, response: str) -> str:
        text_response = None
        try:
            raw_message = response.text
            message = json.loads(raw_message)
            text_response = message.get("response", None) 
        except Exception as e:
            logger.warning(f"[IntentAgent]Error parsing response: {e}")
            text_response =response
        if text_response is not None:
            start = text_response.find('{')
            end = text_response.rfind('}') + 1
            json_str = text_response[start:end]
            next_agent_name = json.loads(json_str)
            return next_agent_name
        return None
        # Implement parsing logic specific to IntentAgent