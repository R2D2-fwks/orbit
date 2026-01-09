from asyncio.log import logger
from pathlib import Path
from src.messages.intent_agent_message import IntentAgentMessage
from src.messages.llm_message import LLMMessage
from src.model.copilot_model import CopilotModel
from src.services.file import FileService
from src.services.repo2Text import Repo2TextService
from thespian.actors import Actor
from src.model.llama_model import LlamaModel
from src.model.model_adapter import ModelAdapter
from toon import encode
import tiktoken
import os
from dotenv import load_dotenv



class TroubleshootingAgent(Actor):
    
    def __init__(self):
        load_dotenv()
        super().__init__()
        # self.model = ModelAdapter(LlamaModel())
        self.model = ModelAdapter(CopilotModel("gpt-4o"))
        self.override_flag = False
        self.max_chunk_tokens= 30000
        self.encoding = tiktoken.encoding_for_model("gpt-4o")
        self.agent_name = "TroubleshootingAgent"
        self.MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
        

    def chunk_content(self, content: str, max_tokens: int):
        return [content[i:i + max_tokens] for i in range(0, len(content), max_tokens)]
    
    def process_chunks(self, chunks, instruction):
        aggregate_response = ""
        for i, chunk in enumerate(chunks):
            logger.info(f"[TroubleshootingAgent] Processing chunk {i+1}/{len(chunks)}")
            response = self.model.chat(chunk, instruction)
            if response is not None:
                aggregate_response += response + "\n"
        return aggregate_response

    def receiveMessage(self, message, sender):
        if (isinstance(message, IntentAgentMessage)):
            query = message.query
            folder_path = Path(__file__).parent
            file_service = FileService()
            repo2text_service = Repo2TextService()
            
            read_instruction = file_service.read_file(folder_path / "troubleshootingGuidelines.md")
            repo_urls = file_service.read_json_file(folder_path / "repo_details.json")
            repo_text = ["BEGIN: \n Here are the details of the repositories:\n"]
            for repo_url in repo_urls.get("repos", []):
                repo_data = repo2text_service.call_service(repo_url, {"max_file_size": self.MAX_FILE_SIZE})
                llm_input_data = encode(repo_data)
                repo_text.append(llm_input_data)
            repo_text.append("User Query: " + query)
            repo_text.append("\n END.")
            complete_prompt = "".join(repo_text)
            complete_repo_tokens = self.encoding.encode(complete_prompt)
            instruction_tokens = self.encoding.encode(read_instruction)
            logger.info(f"[TroubleshootingAgent] Total tokens in prompt: {len(complete_repo_tokens)}")
            logger.info(f"[TroubleshootingAgent] Instruction tokens length: {len(instruction_tokens)}")
            if len(complete_repo_tokens) > self.max_chunk_tokens and self.override_flag == False:
                logger.info(f"[TroubleshootingAgent] Content too large ({len(complete_repo_tokens)} tokens), using chunking")
                chunks = self.chunk_content(complete_prompt, self.max_chunk_tokens)
                response_text = self.process_chunks(chunks, read_instruction)
                response = LLMMessage(response_text)
            else:
                logger.info(f"[TroubleshootingAgent] Content within limit ({len(complete_repo_tokens)} tokens), processing directly")
                response = LLMMessage(self.model.generate(complete_prompt, read_instruction))
            self.send(sender, response)
        else:
            self.send(sender, "Unknown command. Please send 'troubleshoot' to receive troubleshooting assistance.")