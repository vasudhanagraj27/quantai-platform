# QuantAI — Internal AI Enablement Platform

A three-module AI platform built for financial teams at Quantifi Solutions.
Operationalizes AI tools across document intelligence, prompt management, and automated AI news briefing.

**Live App:** [Deploy link here]

---

## What It Does

### Module 1 — Document Intelligence
Upload financial documents (PDFs, reports, regulatory docs) and ask questions in plain English.
The system retrieves the most relevant sections and returns grounded answers with page-level source citations.

Built with RAG (Retrieval Augmented Generation) — the model can only answer from what is in the document. No hallucination.

### Module 2 — Prompt Workbench
A shared prompt management system for AI teams. Write prompts with dynamic `{{variables}}`, test them against real inputs, compare two prompts side by side, and rate outputs.

Includes an **AI Judge** that automatically evaluates two prompt outputs and declares a winner with structured reasoning.

### Module 3 — AI Digest Agent
A LangGraph-powered agent that fetches articles from 7 AI news sources, filters by topic relevance, summarizes each article, and compiles a professional digest report — in under 30 seconds.

Sources: Anthropic, OpenAI, Google DeepMind, HuggingFace, MIT Tech Review, The Gradient, DeepLearning.AI

---

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.10+ |
| LLM | Groq API — llama-3.3-70b-versatile |
| RAG | LangChain · ChromaDB · Sentence Transformers (all-MiniLM-L6-v2) |
| Agents | LangGraph |
| Storage | SQLite · ChromaDB (local vector store) |
| Frontend | Streamlit |
| News Fetching | feedparser · requests |

---

## Project Structure

```
quantai/
├── app.py                          # Landing page
├── pages/
│   ├── 1_Document_Intelligence.py  # Module 1
│   ├── 2_Prompt_Workbench.py       # Module 2
│   └── 3_AI_Digest.py              # Module 3
├── modules/
│   ├── rag/                        # Document processing, embeddings, QA chain
│   ├── prompt_workbench/           # Prompt CRUD, testing, comparison, AI judge
│   └── ai_digest/                  # RSS fetcher, LangGraph pipeline
├── database/
│   ├── db.py                       # SQLite setup
│   └── seed.py                     # Pre-loads 6 demo prompts on first run
└── utils/
    └── helpers.py                  # Shared utilities
```

---

## Running Locally

**1. Clone the repository**
```bash
git clone https://github.com/vasudhanagraj27/quantai.git
cd quantai
```

**2. Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your API key**

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free key at [console.groq.com](https://console.groq.com)

**5. Run the app**
```bash
streamlit run app.py --server.port 8501
```

Open your browser at `http://localhost:8501`

---

## Deploying to Streamlit Cloud

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **Create app** → select this repository → set main file to `app.py`
4. In **Advanced settings → Secrets**, add:
```
GROQ_API_KEY = "your_groq_api_key_here"
```
5. Click **Deploy**

---

## Key Design Decisions

- **Groq over OpenAI** — LPU hardware gives 5-10x faster inference at zero cost
- **Local embeddings** — `all-MiniLM-L6-v2` runs locally with no API cost or latency
- **ChromaDB** — local vector store, no cloud dependency, data stays private
- **LangGraph** — makes the digest pipeline stateful, inspectable, and modular
- **SQLite** — right-sized for this scale, zero configuration
- **Streamlit** — lets Python developers ship production-quality internal tools fast

---

## Built By

**Vasudha Siddapura Nagraj**

[LinkedIn](https://linkedin.com/in/vasudha-siddapura-nagraj) · [GitHub](https://github.com/vasudhanagraj27)
