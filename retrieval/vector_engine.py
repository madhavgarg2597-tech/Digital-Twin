import chromadb
from sentence_transformers import SentenceTransformer

from retrieval.config import (
    CHROMA_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL
)

print("Loading BGE model...")

model = SentenceTransformer(
    EMBEDDING_MODEL
)

print("Model loaded.")

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    COLLECTION_NAME
)

def vector_search(
    query,
    k=10
):

    query_embedding = model.encode(
        f"Represent this sentence for retrieval: {query}",
        normalize_embeddings=True
    )

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=k,
        include=["documents", "metadatas"]
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]

    return [
        {"text": doc, "metadata": meta}
        for doc, meta in zip(docs, metas)
    ]
