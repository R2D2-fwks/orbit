from pymilvus import model


class EmbeddingService:

    def docs_to_vector(self,docs: list,tags:str) -> list:
        embedding_fn = model.DefaultEmbeddingFunction()
        vectors = embedding_fn.encode_documents(docs)
        data = [
            {"id": i, "vector": vectors[i], "text": docs[i], "tags": tags}
            for i in range(len(vectors))
        ]
        return data

    def text_to_vector(self, text: str) -> list:
        embedding_fn = model.DefaultEmbeddingFunction()
        vector = embedding_fn.encode_queries([text])
        return vector