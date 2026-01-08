from abc import abstractmethod

class DatabaseInterface:
    @abstractmethod
    def insert_vectors(self, data: list) -> dict:
        pass
    @abstractmethod
    def search_vectors(self, query_vector:list, top_k: int=40,filter: str=None) -> list:
        pass