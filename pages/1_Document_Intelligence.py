import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import json
from datetime import datetime

from modules.rag.document_processor import load_documents, split_documents
from modules.rag.retriever import add_documents, clear_collection, Document
from modules.rag.qa_chain import answer_question
from utils.helpers import get_groq_api_key, format_sources
from database.db import get_connection, init_db

init_db()

st.set_page_config(page_title="Document Intelligence | QuantAI", page_icon="⚡", layout="wide")

st.title("Financial Document Intelligence")
st.caption("Upload financial documents and ask questions — powered by RAG + Llama 3.3 via Groq")

api_key = get_groq_api_key()

# ── Sidebar: Upload & Manage Documents ────────────────────────────────────────
with st.sidebar:
    st.header("📁 Document Manager")

    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        help="Supports PDF, TXT, and Markdown files",
    )

    if uploaded_files:
        if st.button("Process & Index Documents", type="primary", use_container_width=True):
            with st.spinner("Loading and chunking documents..."):
                docs = load_documents(uploaded_files)
                chunks = split_documents(docs)

            with st.spinner(f"Indexing {len(chunks)} chunks..."):
                add_documents(chunks)

            st.success(f"Indexed {len(chunks)} chunks from {len(uploaded_files)} file(s)")
            st.session_state["docs_loaded"] = True
            st.session_state["doc_names"] = [f.name for f in uploaded_files]

    st.divider()

    if st.button("Clear All Documents", use_container_width=True):
        clear_collection()
        st.session_state.pop("docs_loaded", None)
        st.session_state.pop("doc_names", None)
        st.session_state.pop("chat_history", None)
        st.success("Vector store cleared.")

    if st.session_state.get("doc_names"):
        st.markdown("**Indexed files:**")
        for name in st.session_state["doc_names"]:
            st.markdown(f"- `{name}`")

    st.divider()
    k = st.slider("Top-K chunks to retrieve", min_value=2, max_value=8, value=4)

# ── Main: Chat Interface ───────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if not st.session_state.get("docs_loaded"):
    st.info("Upload and index documents in the sidebar to get started.")
    st.markdown("""
    **What you can upload:**
    - Annual reports & 10-K filings
    - Risk management frameworks
    - Regulatory documents (Basel III, FRTB, etc.)
    - Market research reports
    - Internal trading policies
    """)

# Render chat history
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("Sources", expanded=False):
                st.markdown(msg["sources"])
            st.caption(f"{msg.get('latency_ms', 0)} ms · {msg.get('chunks_used', 0)} chunks retrieved")

# Chat input
question = st.chat_input("Ask a question about your documents...")
if question:
    st.session_state["chat_history"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving and reasoning..."):
            answer, source_docs, latency_ms = answer_question(question, api_key, k=k)

        st.markdown(answer)
        sources_text = format_sources(source_docs)

        with st.expander("Sources", expanded=False):
            st.markdown(sources_text)
        st.caption(f"{latency_ms} ms · {len(source_docs)} chunks retrieved")

    st.session_state["chat_history"].append({
        "role": "assistant",
        "content": answer,
        "sources": sources_text,
        "latency_ms": latency_ms,
        "chunks_used": len(source_docs),
    })

    # Persist to DB
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO rag_history (document_name, question, answer, sources) VALUES (?, ?, ?, ?)",
            (
                ", ".join(st.session_state.get("doc_names", [])),
                question,
                answer,
                sources_text,
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

# ── History Tab ────────────────────────────────────────────────────────────────
st.divider()
with st.expander("Session Q&A History", expanded=False):
    if st.session_state["chat_history"]:
        qa_pairs = [
            m for m in st.session_state["chat_history"] if m["role"] == "user"
        ]
        for i, msg in enumerate(qa_pairs):
            st.markdown(f"**Q{i+1}:** {msg['content']}")
        if st.button("Clear chat history"):
            st.session_state["chat_history"] = []
            st.rerun()
    else:
        st.write("No questions asked yet.")
