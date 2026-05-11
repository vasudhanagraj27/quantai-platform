import re
from groq import Groq
from modules.ai_digest.news_fetcher import fetch_all_feeds

GROQ_MODEL = "llama-3.3-70b-versatile"


def run_digest(api_key: str, topic_focus: str = "AI tools, LLMs, agents, prompt engineering") -> dict:
    client = Groq(api_key=api_key)

    # Step 1: Fetch
    articles = fetch_all_feeds(max_per_source=8)

    # Step 2: Filter
    if not articles:
        return {"articles": [], "filtered": [], "summaries": [], "digest": "No articles fetched."}

    batch_text = "\n".join(
        f"[{i}] {a['source']} | {a['title']} | {a['summary'][:200]}"
        for i, a in enumerate(articles)
    )

    filter_response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{
            "role": "user",
            "content": f"""You are a filter for an AI news digest at Quantifi, a financial risk management firm.

Topic focus: {topic_focus}

From the articles below, return ONLY the index numbers (comma-separated) of articles relevant to:
AI tools, LLMs, agents, prompt engineering, model releases, or AI applied to finance/risk.
Exclude general tech news, company earnings, non-AI topics.

Articles:
{batch_text}

Respond with ONLY comma-separated numbers, e.g.: 0,2,5,7"""
        }],
        max_tokens=200,
        temperature=0.0,
    )

    try:
        indices = [int(x.strip()) for x in filter_response.choices[0].message.content.strip().split(",") if x.strip().isdigit()]
        filtered = [articles[i] for i in indices if i < len(articles)]
    except Exception:
        filtered = articles[:10]

    # Step 3: Summarize
    summaries = []
    for article in filtered[:12]:
        sum_response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{
                "role": "user",
                "content": f"Summarize this AI news article in 2 concise sentences relevant to a financial risk team.\n\nTitle: {article['title']}\nContent: {article['summary']}"
            }],
            max_tokens=150,
            temperature=0.1,
        )
        summaries.append({**article, "ai_summary": sum_response.choices[0].message.content.strip()})

    # Step 4: Compile
    articles_text = "\n\n".join(
        f"**{a['source']}** — {a['title']} ({a['published']})\n{a['ai_summary']}\nURL: {a['url']}"
        for a in summaries
    )

    compile_response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You write concise, professional internal digests."},
            {"role": "user", "content": f"""Write a professional AI digest report for Quantifi's AI team.
Format:
- 2-sentence executive summary
- Articles grouped by theme (Model Releases, Agents & Tooling, AI in Finance)
- Each article as a bullet: bold title, 1-sentence takeaway, source + date
- Closing "What to Watch" with 2-3 forward-looking bullets

Topic focus: {topic_focus}

Articles:
{articles_text}"""}
        ],
        max_tokens=1200,
        temperature=0.2,
    )

    return {
        "articles": articles,
        "filtered": filtered,
        "summaries": summaries,
        "digest": compile_response.choices[0].message.content.strip(),
    }
