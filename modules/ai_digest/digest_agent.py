import json
from typing import TypedDict, Annotated
import operator

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from modules.ai_digest.news_fetcher import fetch_all_feeds

GROQ_MODEL = "llama-3.3-70b-versatile"


# ── State ─────────────────────────────────────────────────────────────────────

class DigestState(TypedDict):
    articles: list[dict]
    filtered: list[dict]
    summaries: list[dict]
    digest: str
    topic_focus: str
    api_key: str


# ── Nodes ─────────────────────────────────────────────────────────────────────

def fetch_node(state: DigestState) -> DigestState:
    articles = fetch_all_feeds(max_per_source=8)
    return {**state, "articles": articles}


def filter_node(state: DigestState) -> DigestState:
    articles = state["articles"]
    topic_focus = state.get("topic_focus", "AI tools, LLMs, agents, prompt engineering")

    if not articles:
        return {**state, "filtered": []}

    llm = ChatGroq(api_key=state["api_key"], model=GROQ_MODEL, temperature=0.0, max_tokens=800)

    batch_text = "\n".join(
        f"[{i}] {a['source']} | {a['title']} | {a['summary'][:200]}"
        for i, a in enumerate(articles)
    )

    prompt = f"""You are a filter for an AI news digest at Quantifi, a financial risk management firm.

Topic focus: {topic_focus}

From the articles below, return ONLY the index numbers (comma-separated) of articles that are
relevant to: AI tools, LLMs, agents, prompt engineering, model releases, or AI applied to finance/risk.
Exclude general tech news, company earnings, non-AI topics.

Articles:
{batch_text}

Respond with ONLY comma-separated numbers, e.g.: 0,2,5,7"""

    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        indices = [int(x.strip()) for x in response.content.strip().split(",") if x.strip().isdigit()]
        filtered = [articles[i] for i in indices if i < len(articles)]
    except Exception:
        filtered = articles[:10]

    return {**state, "filtered": filtered}


def summarize_node(state: DigestState) -> DigestState:
    filtered = state["filtered"]
    if not filtered:
        return {**state, "summaries": []}

    llm = ChatGroq(api_key=state["api_key"], model=GROQ_MODEL, temperature=0.1, max_tokens=200)

    summaries = []
    for article in filtered[:12]:
        prompt = (
            f"Summarize this AI news article in 2 concise sentences relevant to a financial risk team.\n\n"
            f"Title: {article['title']}\nContent: {article['summary']}"
        )
        resp = llm.invoke([HumanMessage(content=prompt)])
        summaries.append({**article, "ai_summary": resp.content.strip()})

    return {**state, "summaries": summaries}


def compile_node(state: DigestState) -> DigestState:
    summaries = state["summaries"]
    topic_focus = state.get("topic_focus", "AI tools and LLMs")

    if not summaries:
        return {**state, "digest": "No relevant articles found for this topic."}

    llm = ChatGroq(api_key=state["api_key"], model=GROQ_MODEL, temperature=0.2, max_tokens=1200)

    articles_text = "\n\n".join(
        f"**{a['source']}** — {a['title']} ({a['published']})\n{a['ai_summary']}\nURL: {a['url']}"
        for a in summaries
    )

    prompt = f"""You are QuantAI's internal AI digest editor for Quantifi's AI team.

Write a professional, scannable digest report from the articles below.
Format it as:
- A 2-sentence executive summary of today's AI landscape
- Grouped sections by theme (e.g., "Model Releases", "Agents & Tooling", "AI in Finance")
- Each article as a bullet: bold title, 1-sentence takeaway, source + date
- A closing "What to Watch" section with 2-3 forward-looking bullets

Topic focus: {topic_focus}

Articles:
{articles_text}"""

    digest = llm.invoke([SystemMessage(content="You write concise, professional internal digests."),
                         HumanMessage(content=prompt)])
    return {**state, "digest": digest.content.strip()}


# ── Graph ─────────────────────────────────────────────────────────────────────

def build_digest_graph():
    graph = StateGraph(DigestState)
    graph.add_node("fetch", fetch_node)
    graph.add_node("filter", filter_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("compile", compile_node)

    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "filter")
    graph.add_edge("filter", "summarize")
    graph.add_edge("summarize", "compile")
    graph.add_edge("compile", END)

    return graph.compile()


def run_digest(api_key: str, topic_focus: str = "AI tools, LLMs, agents, prompt engineering") -> DigestState:
    app = build_digest_graph()
    initial_state: DigestState = {
        "articles": [],
        "filtered": [],
        "summaries": [],
        "digest": "",
        "topic_focus": topic_focus,
        "api_key": api_key,
    }
    return app.invoke(initial_state)
