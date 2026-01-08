

from vector_database.db_interface import DatabaseInterface


class DatabaseAdapter(DatabaseInterface):
    def __init__(self, db_instance):
        self.db = db_instance
    def insert_vectors(self, data: list) -> dict:
        return self.db.insert_vectors(data)
    def search_vectors(self, query_vector:list, top_k: int=40,filter: str=None) -> list:
        return self.db.search_vectors(query_vector, top_k,filter)