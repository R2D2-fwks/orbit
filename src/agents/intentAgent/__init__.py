import json
from src.agent_registry.register import AgentRegistry
from src.messages.intent_agent_message import IntentAgentMessage
from src.messages.query import QueryMessage
from src.model.copilot_model import CopilotModel
from src.services.file import FileService
from thespian.actors import Actor
from src.model.llama_model import LlamaModel
from src.model.model_adapter import ModelAdapter
from pathlib import Path
from loguru import logger
import re

class IntentAgent(Actor):
    def __init__(self):
        super().__init__()
        self.model = ModelAdapter(LlamaModel())
        # self.model = ModelAdapter(CopilotModel("gpt-4o"))
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
            file_path = Path(__file__).parent/ "intentAgentGuidelines.md"
            agent_instructions = FileService().read_file(file_path)
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
        if hasattr(response, 'text'):
            text_response = response.text
        elif hasattr(response, 'message'):
            text_response = response.message
        else:
            text_response = str(response)
        logger.debug(f"[IntentAgent] Parsing response: {text_response[:200]}...")
        json_block_pattern = r'```(?:json)?\s*(\{[^`]*\})\s*```'
        match = re.search(json_block_pattern, text_response, re.DOTALL)
        if match:
            try:
                json_str = match.group(1).strip()
                result = json.loads(json_str)
                logger.info(f"[IntentAgent] Parsed from code block: {result}")
                return result
            except json.JSONDecodeError as e:
                logger.warning(f"[IntentAgent] Failed to parse code block JSON: {e}")
        response_pattern = r'\{\s*"response"\s*:\s*"([^"]+)"\s*\}'
        match = re.search(response_pattern, text_response)
        if match:
            result = {"response": match.group(1)}
            logger.info(f"[IntentAgent] Parsed with regex: {result}")
            return result
        try:
            # Find the first complete JSON object
            start = text_response.find('{')
            if start != -1:
                brace_count = 0
                end = start
                for i, char in enumerate(text_response[start:], start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break
                
                json_str = text_response[start:end]
                result = json.loads(json_str)
                logger.info(f"[IntentAgent] Parsed with brace matching: {result}")
                return result
        except json.JSONDecodeError as e:
            logger.warning(f"[IntentAgent] Failed to parse with brace matching: {e}")
        return None
        # Implement parsing logic specific to IntentAgent