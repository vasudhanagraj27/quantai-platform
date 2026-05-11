import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Always load from project root, regardless of working directory
_ROOT = Path(__file__).parent.parent
load_dotenv(_ROOT / ".env")


def get_groq_api_key() -> str:
    key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not key:
        st.error("GROQ_API_KEY not found. Add it to your .env file or Streamlit secrets.")
        st.stop()
    return key


def format_sources(docs: list) -> str:
    seen = set()
    lines = []
    for doc in docs:
        src = doc.metadata.get("source", "Uploaded Document")
        page = doc.metadata.get("page", "")
        label = f"{src} — page {page + 1}" if page != "" else src
        if label not in seen:
            seen.add(label)
            lines.append(f"- {label}")
    return "\n".join(lines) if lines else "- Uploaded Document"


def chunk_list(lst: list, size: int):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]
