import os
import tempfile
from typing import List

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def load_documents(uploaded_files) -> List[Document]:
    docs = []
    for uploaded_file in uploaded_files:
        suffix = os.path.splitext(uploaded_file.name)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            if suffix == ".pdf":
                loader = PyPDFLoader(tmp_path)
            elif suffix in (".txt", ".md"):
                loader = TextLoader(tmp_path, encoding="utf-8")
            else:
                continue

            raw = loader.load()
            for doc in raw:
                doc.metadata["source"] = uploaded_file.name
            docs.extend(raw)
        finally:
            os.unlink(tmp_path)

    return docs


def split_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(docs)
