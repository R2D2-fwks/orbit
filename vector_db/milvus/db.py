from services.singleton import SingletonClass
from pymilvus import MilvusClient
from vector_db.db_interface import DatabaseInterface

class MilvusDatabase(DatabaseInterface,metaclass=SingletonClass):
    def __init__(self):
        self.client = MilvusClient("agentic_ai.db")
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

