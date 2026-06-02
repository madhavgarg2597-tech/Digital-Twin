import json
import pickle
from pathlib import Path

from rank_bm25 import BM25Okapi

from retrieval.config import BM25_FILE, DOCS_FILE


def build_bm25():

    all_docs = []

    paper_file = Path(
        r"processed_chunks/research papers/documents.json"
    )

    with open(
        paper_file,
        "r",
        encoding="utf-8"
    ) as f:

        papers = json.load(f)

    for item in papers:
        all_docs.append(
            item["page_content"]
        )

    folders = [
        "processed_chunks/blogs",
        "processed_chunks/interviews",
        "processed_chunks/talks"
    ]

    for folder in folders:

        for file in Path(folder).glob("*.json"):

            with open(
                file,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            for item in data:

                all_docs.append(
                    item["text"]
                )

    print(
        f"Loaded {len(all_docs)} docs"
    )

    tokenized_docs = [
        doc.lower().split()
        for doc in all_docs
    ]

    bm25 = BM25Okapi(
        tokenized_docs
    )

    with open(
        BM25_FILE,
        "wb"
    ) as f:

        pickle.dump(
            bm25,
            f
        )

    with open(
        DOCS_FILE,
        "wb"
    ) as f:

        pickle.dump(
            all_docs,
            f
        )

    print(
        "BM25 index saved."
    )


print("Loading BM25 index...")

with open(
    BM25_FILE,
    "rb"
) as f:

    bm25 = pickle.load(f)

with open(
    DOCS_FILE,
    "rb"
) as f:

    all_docs = pickle.load(f)

print(
    f"BM25 loaded: {len(all_docs)} docs"
)


def bm25_search(
    query,
    k=10
):

    tokens = (
        query
        .lower()
        .split()
    )

    scores = bm25.get_scores(
        tokens
    )

    ranked = sorted(
        zip(all_docs, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        doc
        for doc, _
        in ranked[:k]
    ]
