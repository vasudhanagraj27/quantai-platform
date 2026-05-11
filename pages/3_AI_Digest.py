import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import datetime

from modules.ai_digest.digest_agent import run_digest
from modules.ai_digest.news_fetcher import fetch_all_feeds, RSS_SOURCES
from utils.helpers import get_groq_api_key
from database.db import init_db, get_connection

init_db()

st.set_page_config(page_title="AI Digest | QuantAI", page_icon="⚡", layout="wide")

st.title("AI Digest Agent")
st.caption("Automated AI news fetcher, filter, and summarizer — built on LangGraph + Groq")

api_key = get_groq_api_key()

TOPIC_PRESETS = {
    "All AI Tools & LLMs": "AI tools, LLMs, agents, prompt engineering, model releases",
    "AI in Finance & Risk": "AI in finance, risk management, trading, quantitative analysis, fintech AI",
    "Agents & Workflows": "AI agents, agentic workflows, LangGraph, multi-agent systems, tool use",
    "Model Releases & Research": "new model releases, AI research papers, benchmarks, reasoning models",
    "Prompt Engineering": "prompt engineering, prompting techniques, system prompts, RAG improvements",
}

# ── Sidebar Controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Digest Settings")

    preset = st.selectbox("Topic focus", list(TOPIC_PRESETS.keys()))
    custom_topic = st.text_input(
        "Or enter custom focus",
        placeholder="e.g. AI regulation, Claude updates...",
    )
    topic_focus = custom_topic if custom_topic else TOPIC_PRESETS[preset]

    st.divider()
    st.markdown("**Sources monitored:**")
    for s in RSS_SOURCES:
        st.markdown(f"- {s['name']}")

    st.divider()
    st.caption(f"Today: {datetime.now().strftime('%B %d, %Y')}")


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_digest, tab_raw, tab_saved = st.tabs(["Generate Digest", "Raw Feed", "Saved Digests"])


# ── TAB 1: Generate Digest ────────────────────────────────────────────────────
with tab_digest:
    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.markdown(f"**Active focus:** _{topic_focus}_")
    with col_btn:
        run_btn = st.button("Run Agent", type="primary", use_container_width=True)

    if run_btn:
        progress = st.empty()
        status = st.status("Running AI Digest Agent...", expanded=True)

        with status:
            st.write("Fetching articles from RSS feeds...")
            progress_bar = st.progress(0)

            try:
                progress_bar.progress(10)
                st.write("🧠 Filtering relevant articles with LLM...")
                progress_bar.progress(30)

                result = run_digest(api_key=api_key, topic_focus=topic_focus)
                progress_bar.progress(80)

                st.write("Compiling digest report...")
                progress_bar.progress(100)
                status.update(label="Digest ready!", state="complete")

            except Exception as e:
                status.update(label="Agent encountered an error.", state="error")
                st.error(str(e))
                st.stop()

        st.session_state["last_result"] = result
        st.session_state["last_topic"] = topic_focus

    result = st.session_state.get("last_result")
    if result:
        # Metrics row
        m1, m2, m3 = st.columns(3)
        m1.metric("Articles Fetched", len(result.get("articles", [])))
        m2.metric("After Filtering", len(result.get("filtered", [])))
        m3.metric("Summarized", len(result.get("summaries", [])))

        st.divider()

        # Main digest
        st.markdown(result.get("digest", "No digest generated."))

        st.divider()

        # Article cards
        if result.get("summaries"):
            st.subheader("📋 Source Articles")
            for article in result["summaries"]:
                with st.expander(f"**{article['source']}** — {article['title']} · {article['published']}"):
                    st.markdown(f"**AI Summary:** {article['ai_summary']}")
                    st.markdown(f"**Original excerpt:** {article['summary'][:300]}...")
                    st.markdown(f"[Read full article ↗]({article['url']})")

        # Save digest
        st.divider()
        col_save, col_copy = st.columns([1, 3])
        with col_save:
            if st.button("Save this digest", use_container_width=True):
                try:
                    conn = get_connection()
                    conn.execute(
                        "CREATE TABLE IF NOT EXISTS saved_digests (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, digest TEXT, article_count INTEGER, saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
                    )
                    conn.execute(
                        "INSERT INTO saved_digests (topic, digest, article_count) VALUES (?, ?, ?)",
                        (
                            st.session_state.get("last_topic", ""),
                            result.get("digest", ""),
                            len(result.get("summaries", [])),
                        ),
                    )
                    conn.commit()
                    conn.close()
                    st.success("Digest saved.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    else:
        st.info("Click **Run Agent** to generate today's AI digest.")
        st.markdown("""
        **How the agent works:**

        ```
        Fetch RSS Feeds  →  Filter by Topic (LLM)  →  Summarize Each Article  →  Compile Digest Report
        ```

        Built with **LangGraph** — each step is a discrete node in the agent graph.
        Sources: Anthropic, OpenAI, Google DeepMind, HuggingFace, MIT Tech Review, and more.
        """)


# ── TAB 2: Raw Feed ───────────────────────────────────────────────────────────
with tab_raw:
    st.subheader("Live RSS Feed")
    if st.button("Fetch Raw Articles", use_container_width=False):
        with st.spinner("Fetching from all sources..."):
            raw = fetch_all_feeds(max_per_source=6)
        st.session_state["raw_feed"] = raw

    raw = st.session_state.get("raw_feed")
    if raw:
        st.caption(f"{len(raw)} articles fetched")

        source_filter = st.multiselect(
            "Filter by source",
            options=list({a["source"] for a in raw}),
            default=list({a["source"] for a in raw}),
        )
        filtered_raw = [a for a in raw if a["source"] in source_filter]

        rows = [{"Published": a["published"], "Source": a["source"],
                  "Title": a["title"], "URL": a["url"]} for a in filtered_raw]
        st.dataframe(rows, use_container_width=True,
                     column_config={"URL": st.column_config.LinkColumn("URL", display_text="Open ↗")})
    else:
        st.info("Click 'Fetch Raw Articles' to see the live feed.")


# ── TAB 3: Saved Digests ──────────────────────────────────────────────────────
with tab_saved:
    st.subheader("Previously Saved Digests")
    try:
        conn = get_connection()
        conn.execute(
            "CREATE TABLE IF NOT EXISTS saved_digests (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, digest TEXT, article_count INTEGER, saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        )
        rows = conn.execute(
            "SELECT id, topic, article_count, saved_at, digest FROM saved_digests ORDER BY saved_at DESC"
        ).fetchall()
        conn.close()

        if not rows:
            st.info("No saved digests yet. Run the agent and save a digest.")
        else:
            for row in rows:
                with st.expander(f"**{row['saved_at'][:10]}** — {row['topic'][:60]} · {row['article_count']} articles"):
                    st.markdown(row["digest"])
    except Exception as e:
        st.error(str(e))
