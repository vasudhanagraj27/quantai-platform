# QuantAI — Internal AI Enablement Platform

> A production-ready, three-module AI platform built for financial teams at Quantifi Solutions.
> Operationalizes AI tools across document intelligence, prompt management, and automated AI news briefing.

**Live App:** [quantai-platform.streamlit.app](https://quantai-platform.streamlit.app)

&nbsp;|&nbsp;
**Built with:** Python · Groq · BM25 · SQLite · Streamlit

---

## Overview

QuantAI addresses the three core responsibilities of an AI team at a financial firm:

| Module | JD Mapping | What It Does |
|---|---|---|
| Document Intelligence | Delivery — POC to Implementation | Upload financial PDFs, ask questions, get grounded answers with page citations |
| Prompt Workbench | Operationalize AI Tools | Write, test, version, compare, and rate prompts for team use cases |
| AI Digest Agent | Team Enablement | Automatically fetches, filters, and summarizes daily AI news from 7 sources |

---

## Modules

### Module 1 — Document Intelligence

Upload any financial document (PDF, TXT) and ask questions in plain English. The system retrieves the most relevant sections using BM25 search and generates a grounded answer — it cannot hallucinate beyond what is in the document.

- Upload PDFs, TXT, or Markdown files
- Ask questions in plain English
- Answers include page-level source citations
- Adjustable top-K retrieval (2–8 chunks)
- Full Q&A history logged to SQLite

### Module 2 — Prompt Workbench

A shared prompt management system for AI teams. Write prompts with `{{variable}}` placeholders, test them with real inputs, compare two prompts side-by-side, and rate outputs.

- **Library tab** — Create, edit, delete prompts with variable support
- **Test & Refine tab** — Fill variables, run prompts, rate outputs 1–5 stars
- **Compare tab** — A/B test two prompts on the same input
- **AI Judge** — Automatically evaluates both outputs and declares a winner with reasoning
- **History tab** — Full run log with latency metrics and ratings

6 pre-built financial prompts included:
- Risk Report Summarizer (v1 and v2)
- Market Commentary Generator
- Regulatory Q&A Assistant
- Trade Anomaly Explainer
- Client Email Drafter

### Module 3 — AI Digest Agent

An automated AI news briefing system. Fetches articles from 7 sources, filters by topic relevance using an LLM, summarizes each article, and compiles a structured digest report in ~30 seconds.

**Sources monitored:** Anthropic · OpenAI · Google DeepMind · HuggingFace · MIT Tech Review · The Gradient · DeepLearning.AI

**Topic presets:**
- All AI Tools & LLMs
- AI in Finance & Risk
- Agents & Workflows
- Model Releases & Research
- Prompt Engineering

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| LLM | Groq API — llama-3.3-70b-versatile (free) |
| Retrieval | BM25 (rank-bm25) |
| PDF Parsing | pypdf |
| Storage | SQLite (prompts, runs, history, digests) |
| Frontend | Streamlit |
| News Fetching | feedparser · requests · beautifulsoup4 |
| Config | python-dotenv |

---

## Project Structure

```
quantai/
├── app.py                           # Landing page
├── environment.yml                  # Conda env — forces Python 3.11
├── requirements.txt                 # Pip packages
│
├── pages/
│   ├── 1_Document_Intelligence.py
│   ├── 2_Prompt_Workbench.py
│   └── 3_AI_Digest.py
│
├── modules/
│   ├── rag/
│   │   ├── document_processor.py   # PDF loading + chunking
│   │   ├── retriever.py            # BM25 search
│   │   └── qa_chain.py             # Groq QA chain
│   ├── prompt_workbench/
│   │   ├── prompt_manager.py       # SQLite CRUD
│   │   └── prompt_tester.py        # Run, compare, judge prompts
│   └── ai_digest/
│       ├── news_fetcher.py         # RSS feed fetcher
│       └── digest_agent.py         # 4-step pipeline
│
├── database/
│   ├── db.py                       # SQLite setup
│   └── seed.py                     # Pre-loads 6 demo prompts
│
└── utils/
    └── helpers.py                  # API key loader, source formatter
```

---

## Running Locally

**1. Clone the repository**
```bash
git clone https://github.com/vasudhanagraj27/quantai-platform.git
cd quantai-platform
```

**2. Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your Groq API key**

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

## Key Design Decisions

**Groq over OpenAI** — LPU hardware gives 5–10x faster inference at zero cost. Sub-second response times for all LLM calls.

**BM25 over vector embeddings** — Eliminates the need for heavy ML libraries (sentence-transformers, ChromaDB). Pure Python, works on any Python version, zero additional cost.

**SQLite over PostgreSQL** — Right-sized for this use case. Zero configuration, single file, handles all persistence needs.

**Streamlit over React** — Lets a Python developer ship a production-quality interactive web app without frontend context-switching. Ideal for internal AI tooling.

**Direct Groq SDK over LangChain** — Removes heavy framework dependencies, significantly reducing deployment size and startup time.

---

## Deployment

Deployed on **Streamlit Cloud** using a conda `environment.yml` to ensure Python 3.11 compatibility.

To deploy your own instance:
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Create app → select this repo → `app.py` → Python 3.11 in Advanced settings
4. Add secret: `GROQ_API_KEY = "your_key_here"`
5. Deploy

---

## Built By

**Vasudha Siddapura Nagraj**

[LinkedIn](https://linkedin.com/in/vasudha-siddapura-nagraj) · [GitHub](https://github.com/vasudhanagraj27)
