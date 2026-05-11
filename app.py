import streamlit as st
from database.db import init_db
from database.seed import seed_demo_prompts

init_db()
seed_demo_prompts()

st.set_page_config(
    page_title="QuantAI — AI Enablement Platform",
    page_icon="⚡",
    layout="wide",
)

st.title("QuantAI — Internal AI Enablement Platform")
st.caption("Built for Quantifi | Powered by Groq + Llama 3.3 + ChromaDB")

st.markdown("""
---
### What is QuantAI?

QuantAI is an internal AI acceleration platform designed for financial teams at Quantifi.
It operationalizes AI tools across three core workflows:
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### Document Intelligence
    Upload risk reports, regulatory docs, or market research.
    Ask natural language questions and get grounded answers with cited sources.

    **Powered by:** RAG · LangChain · ChromaDB · Llama 3.3
    """)
    st.page_link("pages/1_Document_Intelligence.py", label="Open Document Intelligence →")

with col2:
    st.markdown("""
    ### Prompt Workbench
    Write, test, version, and compare prompts for team-specific use cases.
    Rate outputs and build a shared prompt library.

    **Powered by:** Groq · LangChain · SQLite
    """)
    st.page_link("pages/2_Prompt_Workbench.py", label="Open Prompt Workbench →")

with col3:
    st.markdown("""
    ### AI Digest Agent
    A daily agent that fetches, filters, and summarizes the latest AI tool updates
    relevant to your team — so you stay current without the noise.

    **Powered by:** LangGraph · Groq · RSS Feeds
    """)
    st.page_link("pages/3_AI_Digest.py", label="Open AI Digest →")

st.divider()
st.markdown("""
**Tech Stack:** Python · LangChain · LangGraph · ChromaDB · Groq API · Sentence Transformers · Streamlit · SQLite

*Built by Vasudha Siddapura Nagraj*
""")
