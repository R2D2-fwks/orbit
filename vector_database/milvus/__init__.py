
from pathlib import Path
from pymilvus import MilvusClient
from services.singleton import SingletonClass
from vector_database.db_interface import DatabaseInterface
import os
from dotenv import load_dotenv
class MilvusDatabase(DatabaseInterface,metaclass=SingletonClass):
    def __init__(self):
        load_dotenv()
        self.is_local = os.getenv("IS_LOCAL", "False").lower() == "true"
        file_path = Path(__file__).parent / "temp/agentic_ai.db"
        if self.is_local:
           self.client = MilvusClient(file_path)
        else:
              milvus_host = os.getenv("MILVUS_HOST")
              self.client = MilvusClient(milvus_host)
        self.collection_name = "repo_vectors"
        self.dimension = 768
        self.create_collection(self.collection_name, self.dimension)
        

    def create_collection(self, collection_name: str, dimension: int):
        if not self.client.has_collection(collection_name):
            self.client.create_collection(collection_name, dimension)

    def insert_vectors(self, vectors: list):
        return self.client.insert(self.collection_name, vectors)
    
    def search_vectors(self, query_vectors: list, top_k: int=40,filter:str=None):
        return self.client.search(collection_name=self.collection_name, data=query_vectors, limit=top_k,filter=filter,output_fields=["text", "subject"])