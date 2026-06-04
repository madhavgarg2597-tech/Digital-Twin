import re
from collections import defaultdict

from retrieval.bm25_engine import bm25_search
from retrieval.vector_engine import vector_search

def reciprocal_rank_fusion(
    bm25_results,
    vector_results,
    k=60
):
    """Fuse BM25 and vector results using RRF.
    Each result is a dict: {"text": ..., "metadata": ...}
    We use the text as the dedup key.
    """

    scores = defaultdict(float)
    doc_map = {}

    for rank, doc in enumerate(bm25_results):
        key = doc["text"]
        scores[key] += 1 / (k + rank + 1)
        doc_map[key] = doc

    for rank, doc in enumerate(vector_results):
        key = doc["text"]
        scores[key] += 1 / (k + rank + 1)
        doc_map[key] = doc

    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        doc_map[text]
        for text, _
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
    return "\n\n".join(
        doc["text"] for doc in results
    )

SOURCE_TYPE_LABELS = {
    "blog": "📝 Blog Post",
    "interview": "🎙️ Interview",
    "talk": "🎤 Talk",
    "research_paper": "📄 Research Paper",
    "paper": "📄 Research Paper",
}

SOURCE_FILE_TITLES = {
    "blogsami_manifesto": "A Path Towards Autonomous Machine Intelligence",
    "i_jepa": "I-JEPA: Self-Supervised Learning from Images",
    "v_jepa_2": "V-JEPA 2: Video Joint Embedding Predictive Architecture",
    "lex_258": "Lex Fridman Podcast #258 — Dark Matter of Intelligence",
    "lex_36": "Lex Fridman Podcast #36 — Deep Learning",
    "lex_416": "Lex Fridman Podcast #416 — AI, Open Source & Meta",
    "bigtech_ai_discoveries": "Big Tech AI Discoveries Interview",
    "welch_labs1": "Welch Labs — Deep Learning Series (Part 1)",
    "welch_labs2": "Welch Labs — Deep Learning Series (Part 2)",
}

def _extract_header_field(text, field_name):
    pattern = rf"^{field_name}:\s*(.+)$"
    match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def _is_hash_filename(name):
    clean = name.replace(".pdf", "").replace(".txt", "")
    return len(clean) > 20 and all(c in "0123456789abcdef" for c in clean.lower())

def _extract_title_from_text(text):
    lines = text.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if ":" in line and line.split(":")[0].strip().isupper():
            continue
        if line.startswith("==="):
            continue
        if len(line) > 15:
            title = line[:80]
            if len(line) > 80:
                title += "..."
            return title
    return None

def extract_sources(results):
    """
    Extract deduplicated, readable source citations from result dicts.
    Returns a list of dicts: [{type_label, title, year}, ...]
    """

    seen = set()
    sources = []

    for doc in results:
        text = doc["text"]
        meta = doc.get("metadata", {})

        source_type = meta.get("source_type", "")
        type_label = SOURCE_TYPE_LABELS.get(
            source_type, f"Source"
        )

        title = _extract_header_field(text, "TITLE")

        if not title:
            source_file = meta.get("source_file", "")
            clean_name = source_file.replace(".txt", "").replace(".pdf", "")

            if _is_hash_filename(source_file):
                title = _extract_title_from_text(text)
            else:
                title = SOURCE_FILE_TITLES.get(
                    clean_name,
                    clean_name.replace("_", " ").title() if clean_name else None
                )

        if not title:
            continue

        year = _extract_header_field(text, "YEAR")

        dedup_key = title.lower().strip()
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        sources.append({
            "type_label": type_label,
            "title": title,
            "year": year,
        })

    return sources
