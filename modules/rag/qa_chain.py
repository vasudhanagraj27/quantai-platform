import time
from typing import Tuple, List

from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from modules.rag.retriever import similarity_search

GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are QuantAI, an expert financial analyst assistant for Quantifi — a leading risk management and analytics firm.

You answer questions using ONLY the context provided from uploaded financial documents.
Be precise, professional, and cite specific details from the context.
If the context does not contain enough information to answer, say so clearly — do not hallucinate.

Context:
{context}"""

HUMAN_PROMPT = "{question}"


def format_context(docs: List[Document]) -> str:
    return "\n\n---\n\n".join(
        f"[Source: {doc.metadata.get('source', 'Document')}, Page {doc.metadata.get('page', 0) + 1}]\n{doc.page_content}"
        for doc in docs
    )


def build_chain(api_key: str):
    llm = ChatGroq(
        api_key=api_key,
        model=GROQ_MODEL,
        temperature=0.1,
        max_tokens=1024,
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT),
    ])
    return prompt | llm | StrOutputParser()


def answer_question(
    question: str,
    api_key: str,
    k: int = 4,
) -> Tuple[str, List[Document], int]:
    docs = similarity_search(question, k=k)

    if not docs:
        return "No relevant documents found. Please upload documents first.", [], 0

    context = format_context(docs)
    chain = build_chain(api_key)

    start = time.time()
    answer = chain.invoke({"context": context, "question": question})
    latency_ms = int((time.time() - start) * 1000)

    return answer, docs, latency_ms
