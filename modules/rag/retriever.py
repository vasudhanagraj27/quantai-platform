import os
import pickle
from typing import List

from rank_bm25 import BM25Okapi
from langchain_core.documents import Document

DOCS_PATH = os.path.join(os.path.dirname(__file__), "../../stored_docs.pkl")


def _tokenize(text: str) -> list:
    return text.lower().split()


def add_documents(docs: List[Document], **kwargs):
    existing = _load_docs()
    all_docs = existing + docs
    with open(DOCS_PATH, "wb") as f:
        pickle.dump(all_docs, f)


def _load_docs() -> List[Document]:
    if os.path.exists(DOCS_PATH):
        with open(DOCS_PATH, "rb") as f:
            return pickle.load(f)
    return []


def similarity_search(query: str, k: int = 4, **kwargs) -> List[Document]:
    docs = _load_docs()
    if not docs:
        return []
    corpus = [_tokenize(d.page_content) for d in docs]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(_tokenize(query))
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    return [docs[i] for i in top_indices]


def clear_collection():
    if os.path.exists(DOCS_PATH):
        os.remove(DOCS_PATH)


def get_embeddings():
    return None
