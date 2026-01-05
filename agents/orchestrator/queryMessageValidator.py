from agents.intentAgent import IntentAgent
from chain.baseHandler import BaseHandler
from messages.query import QueryMessage
from loguru import logger

class QueryMessageValidator(BaseHandler):
    def handle(self, context):
        message,orchestrator_self,sender = context
        if(isinstance(message,QueryMessage)):
            intent_agent_addr = orchestrator_self.createActor(IntentAgent,globalName="IntentAgent")
            orchestrator_self.send(intent_agent_addr, message)
            logger.info("[QueryMessageValidator]: Sent QueryMessage to IntentAgent , message: {}", message)
            return context
        return super().handle(context)
