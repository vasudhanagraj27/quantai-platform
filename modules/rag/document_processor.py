import os
import tempfile
from typing import List

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def load_documents(uploaded_files) -> List[Document]:
    docs = []
    for uploaded_file in uploaded_files:
        suffix = os.path.splitext(uploaded_file.name)[-1].lower()
        content = uploaded_file.read()

        if suffix == ".pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            try:
                reader = PdfReader(tmp_path)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    if text.strip():
                        docs.append(Document(
                            page_content=text,
                            metadata={"source": uploaded_file.name, "page": i}
                        ))
            finally:
                os.unlink(tmp_path)

        elif suffix in (".txt", ".md"):
            text = content.decode("utf-8", errors="ignore")
            docs.append(Document(
                page_content=text,
                metadata={"source": uploaded_file.name, "page": 0}
            ))

    return docs


def split_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(docs)
