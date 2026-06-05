# 🤖 Yann LeCun Digital Twin

An AI-powered digital twin of Yann LeCun that answers questions the way he would — grounded in his actual research papers, blog posts, talks, and interviews. Built with a hybrid retrieval pipeline, cross-encoder reranking, automated memory extraction, and Gemini 2.5 Flash as the reasoning engine. Features a premium dark-themed Streamlit chat UI with multi-conversation support.

---

## ✨ Features

- 🔍 **Hybrid Search** — combines BM25 keyword search + BGE semantic vector search
- 🔀 **Reciprocal Rank Fusion (RRF)** — merges results from both retrievers intelligently
- 🎯 **Cross-Encoder Reranking** — re-scores and re-orders retrieved chunks for maximum relevance
- 🧠 **Dual Memory System** — short-term (session) + long-term (persistent JSON) memory
- 🤖 **Automated Memory Extraction** — background LLM agent silently learns and remembers facts about you across conversations
- 🧠 **Memory Dashboard** — interactive popup to view long-term and short-term memory state in real time
- 📊 **Live RAGAS Evaluation** — real-time, on-the-fly evaluation of Faithfulness and Relevancy for single answers
- 💬 **Multi-Chat Support** — create, switch between, and delete multiple conversation threads
- 🎛️ **Response Length Control** — toggle between Short, Medium, and Detailed response modes
- 📚 **Source Citations** — expandable source chips beneath each response showing which papers/blogs/talks were used
- 🗣️ **Persona Prompt Engineering** — dedicated `system_prompt.py` instructs Gemini to respond as Yann LeCun
- 🎨 **Premium Dark UI** — glassmorphism effects, gradient accents, smooth animations, and a polished chat layout

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────┐
│              ask_twin.py                    │
│  ┌───────────────────────────────────┐      │
│  │         Memory Router             │      │
│  │    (is this a memory query?)      │      │
│  └──────────────┬────────────────────┘      │
│                 │                            │
│        No       │         Yes               │
│  ┌──────────────▼────────┐  ┌────────────┐  │
│  │   Hybrid Retrieval    │  │ Skip to    │  │
│  │   (BM25 + Vector)     │  │ Memory     │  │
│  └──────────────┬────────┘  └────────────┘  │
└─────────────────┼───────────────────────────┘
                  │
    ┌─────────────▼──────────────┐
    │       retrieval/           │
    │                            │
    │  bm25_engine.py            │  ← BM25 keyword search
    │  vector_engine.py          │  ← BGE embedding + ChromaDB
    │          │                 │
    │  fusion.py                 │  ← RRF merges both results
    │          │                 │
    │  reranker.py               │  ← CrossEncoder re-scores
    └──────────┬─────────────────┘
               │
    ┌──────────▼───────────────────────────────┐
    │          Gemini 2.5 Flash                │
    │                                          │
    │  System Prompt (system_prompt.py)         │
    │  Long-Term Memory  +  Conversation Hist.  │
    │  Retrieved Context  +  User Query         │
    └──────────┬───────────────────────────────┘
               │
    ┌──────────▼──────────────────────┐
    │         Response                │
    │  (saved to short-term memory)   │
    └──────────┬──────────────────────┘
               │
    ┌──────────▼──────────────────────┐
    │  Background Memory Extraction   │
    │  (threaded Gemini 2.5 Flash)    │
    │  Extracts user facts → saves    │
    │  to long_term_memory.json       │
    └─────────────────────────────────┘
```

---

## 📁 Project Structure

```
Digital-Twin/
│
├── app.py                    # Streamlit chat UI (premium dark theme, multi-chat, memory dashboard)
├── ask_twin.py               # Core orchestration: retrieval → generation → memory extraction
├── memory.py                 # Short-term + long-term memory management
├── system_prompt.py          # Yann LeCun persona system prompt (separated for modularity)
├── create_chroma_db.py       # One-time script: build ChromaDB + BM25 indexes
├── test_retrieval.py         # Retrieval pipeline entry point + test runner
├── long_term_memory.json     # Persistent long-term user facts (auto-populated)
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
| **Short-term** | Streamlit `session_state` | Per chat session | Last 6 messages |
| **Long-term** | `long_term_memory.json` | Persistent across all chats | Unlimited |

### Memory Router
The **Memory Router** in `ask_twin.py` detects self-referential queries (e.g. *"what am I building?"*, *"what database am I using?"*) and skips retrieval entirely, serving answers directly from long-term memory.

### Automated Memory Extraction
After every response, a **background thread** sends the latest `(user_query, assistant_response)` pair to Gemini 2.5 Flash with a specialized extraction prompt. If the model detects a new persistent fact about the user (e.g., their name, preferences, project details), it automatically appends it to `long_term_memory.json` via the `remember()` function — without slowing down the chat response.

### Memory Dashboard
The UI includes an interactive **🧠 Memory Dashboard** popup (accessible from the sidebar) that displays:
- **Long-Term Memory** — all persistent facts learned about you, with a clear button
- **Short-Term Memory** — the rolling context window (last 6 messages) for the active chat

---

## 🎨 UI Features (`app.py`)

The Streamlit frontend features a premium dark-themed interface:

- **Multi-Chat Sidebar** — create new conversations, switch between them, and delete old ones
- **Response Length Selector** — choose between Short (2-3 sentences), Medium (2-3 paragraphs), or Detailed (full depth)
- **Source Citation Chips** — expandable source references under each response showing the paper/blog/talk title, type, and year
- **Suggestion Chips** — pre-built quick-start questions on the welcome screen
- **Glassmorphism Design** — frosted-glass sidebar, gradient header accents, smooth hover animations, and custom scrollbars
- **Live Evaluation Button** — instantly grade the quality of the Yann LeCun twin's response.

---

## 📊 Live RAGAS Evaluation (`eval_live.py`)

Every response includes an **"Evaluate"** button. Clicking it triggers an on-the-fly, ground-truth-free RAGAS evaluation using a secondary LLM grader (via Groq `llama-3.3-70b-versatile`). It computes:

1. **Faithfulness**: Did the AI stick strictly to the retrieved context, or did it hallucinate? (Higher is better).
2. **Answer Relevancy**: Did the AI directly answer the user's prompt?

> [!NOTE]
> **Why is Answer Relevancy sometimes low?**
> RAGAS calculates relevancy by backwards-generating the original question from the answer. Because the `system_prompt.py` gives Yann LeCun a very **strong, opinionated, conversational persona**, the answer contains conversational filler ("In my view...", "I disagree with that framing"). This confuses the mathematical grader, resulting in artificially lower relevancy scores (e.g., 0.45). As long as Faithfulness is high, a low relevancy score simply means the persona is working!

---

## 🤖 Persona Prompt (`system_prompt.py`)

The system prompt is maintained in a dedicated module and instructs Gemini to:
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
pip install streamlit google-genai python-dotenv langchain-text-splitters \
            chromadb sentence-transformers rank-bm25
```

### 3. Configure your API key
```bash
cp .env.example .env
# Open .env and add your API keys:
# GEMINI_API_KEY=your_gemini_key_here
# GROQ_API_KEY=your_groq_key_here  (Required for the Live Evaluation feature)
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
| LLM (Generation) | Gemini 2.5 Flash (`google-genai`) |
| LLM (Memory Extraction) | Gemini 2.5 Flash (background thread) |
| LLM (Evaluation Grader) | Groq LLaMA 3.3 70B (`langchain-groq`) |
| Evaluation Framework | RAGAS (`ragas`) |
| Vector DB | ChromaDB |
| Embeddings | `BAAI/bge-base-en-v1.5` (SentenceTransformers) |
| Keyword Search | BM25Okapi (`rank-bm25`) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Text Splitting | LangChain `RecursiveCharacterTextSplitter` |
| UI | Streamlit (custom dark theme) |

---

## 🔒 Security

- `.env` is listed in `.gitignore` and will **never** be committed
- Use `.env.example` as a template — it contains no real credentials
- Large binary index files (`bm25_index.pkl`, `documents.pkl`) and the local ChromaDB (`yann_lecun_db/`) are gitignored
- Research paper PDFs and design docs are kept local-only and excluded from the repository

---

## 📄 License

MIT