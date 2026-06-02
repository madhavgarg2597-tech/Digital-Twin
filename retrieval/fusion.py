from collections import defaultdict

from retrieval.bm25_engine import bm25_search
from retrieval.vector_engine import vector_search


def reciprocal_rank_fusion(
    bm25_results,
    vector_results,
    k=60
):

    scores = defaultdict(
        float
    )

    for rank, doc in enumerate(
        bm25_results
    ):

        scores[doc] += (
            1 / (k + rank + 1)
        )

    for rank, doc in enumerate(
        vector_results
    ):

        scores[doc] += (
            1 / (k + rank + 1)
        )

    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        doc
        for doc, _
        in ranked
    ]


def hybrid_search(
    query,
    top_k=5
):

    bm25_results = bm25_search(
        query,
        k=10
    )

    vector_results = vector_search(
        query,
        k=10
    )

    fused_results = (
        reciprocal_rank_fusion(
            bm25_results,
            vector_results
        )
    )

    return fused_results[:top_k]


def build_context(results):

    context = "\n\n".join(results)

    return context
