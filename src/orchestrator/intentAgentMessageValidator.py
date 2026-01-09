from src.agents.agentRegistry import AgentRegistry
from src.chain.baseHandler import BaseHandler
from src.messages.intent_agent_message import IntentAgentMessage
from loguru import logger

class IntentAgentMessageValidator(BaseHandler):
    def handle(self, context):
        message, orchestrator_self,sender = context
        if(isinstance(message, IntentAgentMessage)):
            agent_name = message.message.get("response", None)
            logger.info("[IntentAgentMessageValidator] Extracted agent name: {}", agent_name)
            if agent_name is not None:
                agent = AgentRegistry().get_agent(agent_name)
                logger.info("[IntentAgentMessageValidator] Creating Agent: {}", agent_name)
                action_agent_addr = orchestrator_self.createActor(agent["agent"], globalName=agent_name)
                orchestrator_self.send(action_agent_addr, message)
                logger.info("[IntentAgentMessageValidator] Validated IntentAgentMessage: {}", agent_name)
                return context
        return super().handle(context)
    