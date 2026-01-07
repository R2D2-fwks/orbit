from asyncio.log import logger
from pathlib import Path
from messages.intent_agent_message import IntentAgentMessage
from messages.llm_message import LLMMessage
from model.copilot_model import CopilotModel
from services.file import FileService
from services.repo2Text import Repo2TextService
from thespian.actors import Actor
from model.llama_model import LlamaModel
from model.model_adapter import ModelAdapter
from toon import encode
import tiktoken

class TroubleshootingAgent(Actor):
    def __init__(self):
        super().__init__()
        # self.model = ModelAdapter(LlamaModel())
        self.max_chunk_tokens= 10000
        self.encoding = tiktoken.encoding_for_model("gpt-4o")
        self.model = ModelAdapter(CopilotModel("gpt-4o"))
        self.agent_name = "TroubleshootingAgent"

    def chunk_content(self, content: str, max_tokens: int):
        sentences = content.split('###############')
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            test_chunk = current_chunk + sentence + '###############'
            token_count = len(self.encoding.encode(test_chunk))
            if token_count <= max_tokens:
                current_chunk = test_chunk
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + '###############'
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks
    
    def process_chunks(self, chunks, instruction):
        aggregate_response = ""
        for i, chunk in enumerate(chunks):
            logger.info(f"[TroubleshootingAgent] Processing chunk {i+1}/{len(chunks)}")
            response = self.model.generate(chunk, instruction)
            if response is not None:
                aggregate_response += response + "\n"
        return aggregate_response

    def receiveMessage(self, message, sender):
        if (isinstance(message, IntentAgentMessage)):
            query = message.query
            folder_path = Path(__file__).parent
            file_service = FileService()
            repo2text_service = Repo2TextService()
            existing_thread_id = self.model.get_latest_thread()
            if existing_thread_id:
                self.model.delete_thread(existing_thread_id)
            read_instruction = file_service.read_file(folder_path / "troubleshootingGuidelines.md")
            repo_urls = file_service.read_json_file(folder_path / "repo_details.json")
            file_service.write_file(folder_path / "repo_texts.txt", "BEGIN: \n Here are the details of the repositories:\n")
            for repo_url in repo_urls.get("repos", []):
                repo_data = repo2text_service.call_service(repo_url)
                llm_input_data = encode(repo_data)
                file_service.append_file(folder_path / "repo_texts.txt", llm_input_data)
                file_service.append_file(folder_path / "repo_texts.txt", "\n###############\n")
            file_service.append_file(folder_path / "repo_texts.txt", "\n User Query: " + query + "\n END.")  
            complete_prompt = file_service.read_file(folder_path / "repo_texts.txt")
            content_tokens = self.encoding.encode(complete_prompt)
            instruction_tokens = self.encoding.encode(read_instruction)
            logger.info(f"[TroubleshootingAgent] Total tokens in prompt: {len(content_tokens)}")
            logger.info(f"[TroubleshootingAgent] Instruction tokens length: {len(instruction_tokens)}")
            if len(content_tokens) > self.max_chunk_tokens:
                logger.info(f"[TroubleshootingAgent] Content too large ({len(content_tokens)} tokens), using chunking")
                chunks = self.chunk_content(complete_prompt, self.max_chunk_tokens)
                response_text = self.process_chunks(chunks, read_instruction)
                response = LLMMessage(response_text)
            else:
                logger.info(f"[TroubleshootingAgent] Content within limit ({len(content_tokens)} tokens), processing directly")
                response = LLMMessage(self.model.generate(complete_prompt, read_instruction))
            self.send(sender, response)
        else:
            self.send(sender, "Unknown command. Please send 'troubleshoot' to receive troubleshooting assistance.")