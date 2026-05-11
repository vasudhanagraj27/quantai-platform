import feedparser
import requests
from datetime import datetime, timezone
from typing import Optional

RSS_SOURCES = [
    {"name": "Anthropic", "url": "https://www.anthropic.com/blog/rss.xml"},
    {"name": "OpenAI", "url": "https://openai.com/news/rss.xml"},
    {"name": "Google DeepMind", "url": "https://deepmind.google/blog/rss.xml"},
    {"name": "HuggingFace", "url": "https://huggingface.co/blog/feed.xml"},
    {"name": "MIT Tech Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/"},
    {"name": "The Gradient", "url": "https://thegradient.pub/rss/"},
    {"name": "DeepLearning.AI", "url": "https://www.deeplearning.ai/the-batch/feed/"},
]

HEADERS = {"User-Agent": "QuantAI-Digest/1.0 (internal tool)"}


def _parse_date(entry) -> Optional[datetime]:
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def fetch_feed(source: dict, max_articles: int = 10) -> list[dict]:
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=8)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
    except Exception:
        return []

    articles = []
    for entry in feed.entries[:max_articles]:
        pub_date = _parse_date(entry)
        summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
        # strip HTML tags simply
        import re
        summary = re.sub(r"<[^>]+>", " ", summary).strip()
        summary = re.sub(r"\s+", " ", summary)[:600]

        articles.append({
            "source": source["name"],
            "title": getattr(entry, "title", "Untitled"),
            "url": getattr(entry, "link", ""),
            "summary": summary,
            "published": pub_date.strftime("%Y-%m-%d") if pub_date else "Unknown",
            "published_dt": pub_date,
        })
    return articles


def fetch_all_feeds(max_per_source: int = 8) -> list[dict]:
    all_articles = []
    for source in RSS_SOURCES:
        articles = fetch_feed(source, max_articles=max_per_source)
        all_articles.extend(articles)

    # sort by date descending, unknowns last
    all_articles.sort(
        key=lambda a: a["published_dt"] or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    # remove the datetime object (not JSON serializable)
    for a in all_articles:
        a.pop("published_dt", None)

    return all_articles
