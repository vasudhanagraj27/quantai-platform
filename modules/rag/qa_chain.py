import time
from typing import Tuple, List
from groq import Groq
from modules.rag.retriever import similarity_search, Document

GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are QuantAI, an expert financial analyst assistant for Quantifi — a leading risk management and analytics firm.

You answer questions using ONLY the context provided from uploaded financial documents.
Be precise, professional, and cite specific details from the context.
If the context does not contain enough information to answer, say so clearly — do not hallucinate.

Context:
{context}"""


def format_context(docs: List[Document]) -> str:
    return "\n\n---\n\n".join(
        f"[Source: {doc.metadata.get('source', 'Document')}, Page {doc.metadata.get('page', 0) + 1}]\n{doc.page_content}"
        for doc in docs
    )


def answer_question(question: str, api_key: str, k: int = 4) -> Tuple[str, List[Document], int]:
    docs = similarity_search(question, k=k)

    if not docs:
        return "No relevant documents found. Please upload documents first.", [], 0

    context = format_context(docs)
    client = Groq(api_key=api_key)

    start = time.time()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
            {"role": "user", "content": question},
        ],
        max_tokens=1024,
        temperature=0.1,
    )
    latency_ms = int((time.time() - start) * 1000)
    answer = response.choices[0].message.content

    return answer, docs, latency_ms
