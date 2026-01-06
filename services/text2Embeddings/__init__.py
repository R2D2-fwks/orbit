from pymilvus import model

def docs_to_vector(docs: list,tags:str) -> list:
    embedding_fn = model.DefaultEmbeddingFunction()
    vectors = embedding_fn.encode_documents(docs)
    data = [
        {"id": i, "vector": vectors[i], "text": docs[i], "tags": tags}
        for i in range(len(vectors))
    ]
    return data


def text_to_vector(text: str) -> list:
    embedding_fn = model.DefaultEmbeddingFunction()
    vector = embedding_fn.encode_queries([text])
    return vector

