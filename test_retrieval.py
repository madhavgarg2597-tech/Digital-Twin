from retrieval.fusion import hybrid_search, build_context
from retrieval.reranker import rerank_results

if __name__ == "__main__":

    query = "What is JEPA?"

    retrieved_chunks = hybrid_search(
        query,
        top_k=20
    )

    reranked_chunks = rerank_results(
        query,
        retrieved_chunks,
        top_k=5
    )

    context = build_context(
        reranked_chunks
    )

    print("\n")
    print("=" * 80)
    print("FINAL CONTEXT")
    print("=" * 80)
    print(context)

    for i, doc in enumerate(
        reranked_chunks,
        start=1
    ):

        print("\n")
        print("=" * 80)
        print(f"RERANKED RESULT {i}")
        print("=" * 80)

        print(doc[:1200])