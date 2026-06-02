# 🤖 Yann LeCun Digital Twin

An AI-powered digital twin of Yann LeCun that answers questions the way he would — grounded in his actual research papers, blog posts, talks, and interviews. Built with a hybrid retrieval pipeline, cross-encoder reranking, dual memory system, and Gemini 2.5 Flash as the reasoning engine.

---

## ✨ Features

- 🔍 **Hybrid Search** — combines BM25 keyword search + BGE semantic vector search
- 🔀 **Reciprocal Rank Fusion (RRF)** — merges results from both retrievers intelligently
- 🎯 **Cross-Encoder Reranking** — re-scores and re-orders retrieved chunks for maximum relevance
- 🧠 **Dual Memory System** — short-term (session) + long-term (persistent JSON) memory
- 🗣️ **Persona Prompt Engineering** — Gemini 2.5 Flash is instructed to respond as Yann LeCun
- 🖥️ **Streamlit Chat UI** — clean chat interface with conversation history

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────┐
│           ask_twin.py               │
│  ┌─────────────────────────────┐    │
│  │     Memory Router           │    │
│  │  (is this a memory query?)  │    │
│  └────────────┬────────────────┘    │
│               │                     │
│      No       │       Yes           │
│  ┌────────────▼──────┐  ┌────────┐  │
│  │  Hybrid Retrieval │  │ Skip   │  │
│  └────────────┬──────┘  └────────┘  │
└───────────────┼─────────────────────┘
                │
    ┌───────────▼────────────┐
    │    retrieval/           │
    │                         │
    │  bm25_engine.py         │  ← BM25 keyword search
    │  vector_engine.py       │  ← BGE embedding + ChromaDB
    │         │                │
    │  fusion.py              │  ← RRF merges both results
    │         │                │
    │  reranker.py            │  ← CrossEncoder re-scores
    └───────────┬─────────────┘
                │
    ┌───────────▼─────────────────────────┐
    │           Gemini 2.5 Flash          │
    │                                     │
    │  System Prompt  +  Long-Term Mem    │
    │  Conversation History               │
    │  Retrieved Context  +  User Query   │
    └───────────┬─────────────────────────┘
                │
    ┌───────────▼──────────┐
    │      Response        │
    │  (saved to memory)   │
    └──────────────────────┘
```

---

## 📁 Project Structure

```
Yann le Cun/
│
├── app.py                    # Streamlit chat UI
├── ask_twin.py               # Core orchestration logic
├── memory.py                 # Short-term + long-term memory
├── create_chroma_db.py       # One-time script: build ChromaDB index
├── test_retrieval.py         # Retrieval pipeline entry point + test runner
│
├── retrieval/                # Modular retrieval package
│   ├── __init__.py
│   ├── config.py             # Shared constants (paths, model names)
│   ├── bm25_engine.py        # BM25 index builder + keyword search
│   ├── vector_engine.py      # BGE embeddings + ChromaDB vector search
│   ├── reranker.py           # CrossEncoder reranker
│   └── fusion.py             # RRF fusion + hybrid_search + build_context
│
├── processed_chunks/         # Pre-chunked knowledge base (JSON)
│   ├── blogs/
│   ├── interviews/
│   ├── talks/
│   └── research papers/
│
├── .env                      # 🔒 Your API key (never committed)
├── .env.example              # Safe template for .env
├── .gitignore
└── README.md
```

---

## 🔍 Retrieval Pipeline — Step by Step

### 1. Knowledge Ingestion
Raw text from research papers, blog posts, talks, and interviews is split into overlapping chunks (1000 tokens, 200 overlap) using LangChain's `RecursiveCharacterTextSplitter` and stored as JSON files in `processed_chunks/`.

### 2. Index Building (`create_chroma_db.py`)
Run once to build two indexes:
- **ChromaDB** — dense vector index using `BAAI/bge-base-en-v1.5` embeddings
- **BM25** — sparse keyword index using `BM25Okapi` (saved as `.pkl`)

### 3. Hybrid Search (`retrieval/fusion.py`)
At query time, both indexes are searched in parallel:
- `bm25_search()` → top-10 keyword matches
- `vector_search()` → top-10 semantic matches

Results are merged using **Reciprocal Rank Fusion (RRF)** — a rank-based fusion technique that rewards documents appearing highly in both lists.

### 4. Reranking (`retrieval/reranker.py`)
The fused candidate set is passed to a `cross-encoder/ms-marco-MiniLM-L-6-v2` CrossEncoder, which scores each `(query, chunk)` pair directly and returns the top-8 most relevant chunks.

### 5. Context Assembly
The top-8 reranked chunks are joined into a single context string and injected into the Gemini prompt.

---

## 🧠 Memory System (`memory.py`)

| Type | Storage | Scope | Capacity |
|---|---|---|---|
| **Short-term** | Streamlit `session_state` | Current session only | Last 6 messages |
| **Long-term** | `long_term_memory.json` | Persistent across sessions | Unlimited |

The **Memory Router** in `ask_twin.py` detects self-referential queries (e.g. *"what am I building?"*, *"what database am I using?"*) and skips retrieval entirely, serving answers directly from long-term memory.

---

## 🤖 Persona Prompt

The system prompt instructs Gemini to:
- Respond in first person as Yann LeCun
- Be technically precise, direct, and slightly skeptical
- Correct misconceptions in questions
- Distinguish between architectures, training objectives, and learning paradigms
- Default to concise 2-3 paragraph answers unless asked for detail

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/madhavgarg2597-tech/Digital-Twin.git
cd Digital-Twin
```

### 2. Install dependencies
```bash
pip install streamlit google-generativeai python-dotenv langchain-text-splitters \
            chromadb sentence-transformers rank-bm25
```

### 3. Configure your API key
```bash
cp .env.example .env
# Open .env and add your Gemini API key
```

### 4. Build the indexes (run once)
```bash
python create_chroma_db.py
```

> This builds the ChromaDB vector index and the BM25 keyword index from the `processed_chunks/` data.

### 5. Run the app
```bash
streamlit run app.py
```

---

## 🧪 Test the Retrieval Pipeline

Run retrieval standalone to verify everything is working:
```bash
python test_retrieval.py
```
This runs a test query (`"What is JEPA?"`) through the full hybrid search → rerank pipeline and prints the top results.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| LLM | Gemini 2.5 Flash (`google-genai`) |
| Vector DB | ChromaDB |
| Embeddings | `BAAI/bge-base-en-v1.5` (SentenceTransformers) |
| Keyword Search | BM25Okapi (`rank-bm25`) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Text Splitting | LangChain `RecursiveCharacterTextSplitter` |
| UI | Streamlit |

---

## 🔒 Security

- `.env` is listed in `.gitignore` and will **never** be committed
- Use `.env.example` as a template — it contains no real credentials
- Large binary index files (`bm25_index.pkl`, `documents.pkl`) and the local ChromaDB (`yann_lecun_db/`) are also gitignored

---

## 📄 License

MIT