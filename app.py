import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

st.set_page_config(
    page_title="QuantAI — AI Enablement Platform",
    page_icon="⚡",
    layout="wide",
)

try:
    from database.db import init_db
    from database.seed import seed_demo_prompts
    init_db()
    seed_demo_prompts()
except Exception as e:
    st.error(f"Startup error: {e}")

st.title("QuantAI — Internal AI Enablement Platform")
st.caption("Built for Quantifi | Powered by Groq + Llama 3.3")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### Document Intelligence
    Upload financial documents and ask questions in plain English.
    Answers are grounded with page-level source citations.

    **Powered by:** BM25 Retrieval · Groq · Llama 3.3
    """)
    st.page_link("pages/1_Document_Intelligence.py", label="Open Document Intelligence →")

with col2:
    st.markdown("""
    ### Prompt Workbench
    Write, test, version, and compare prompts for team-specific use cases.
    Rate outputs and build a shared prompt library.

    **Powered by:** Groq · SQLite
    """)
    st.page_link("pages/2_Prompt_Workbench.py", label="Open Prompt Workbench →")

with col3:
    st.markdown("""
    ### AI Digest Agent
    Fetches, filters, and summarizes the latest AI tool updates
    relevant to your team — automatically.

    **Powered by:** Groq · RSS Feeds
    """)
    st.page_link("pages/3_AI_Digest.py", label="Open AI Digest →")

st.divider()
st.markdown("**Built by Vasudha Siddapura Nagraj**")
