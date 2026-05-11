from database.db import init_db, get_connection

DEMO_PROMPTS = [
    {
        "name": "Risk Report Summarizer",
        "use_case": "Risk Summarization",
        "prompt_text": "You are a senior risk analyst at Quantifi.\n\nSummarize the following risk report in exactly 3 bullet points. Each bullet should highlight a key risk, its severity, and the recommended mitigation.\n\nReport:\n{{report_text}}",
        "notes": "Use for daily risk briefings. Keep bullets under 30 words each.",
    },
    {
        "name": "Market Commentary Generator",
        "use_case": "Market Commentary",
        "prompt_text": "Write a professional 2-paragraph market commentary for {{date}} based on the following data:\n\n{{market_data}}\n\nTone: concise, institutional. Audience: portfolio managers.",
        "notes": "Tested on equities and FX data. Adjust tone instruction for retail clients.",
    },
    {
        "name": "Regulatory Q&A Assistant",
        "use_case": "Regulatory Q&A",
        "prompt_text": "You are a regulatory compliance expert specializing in {{regulation}} (e.g. Basel III, FRTB, MiFID II).\n\nAnswer the following question clearly and cite the relevant article or section if possible:\n\n{{question}}\n\nIf you are unsure, say so explicitly.",
        "notes": "Always verify output against official regulatory texts before use.",
    },
    {
        "name": "Trade Anomaly Explainer",
        "use_case": "Trade Analysis",
        "prompt_text": "Analyze the following trade data and identify any anomalies, outliers, or patterns that warrant review:\n\n{{trade_data}}\n\nFor each anomaly found, explain: what it is, why it might be flagged, and what action to take.",
        "notes": "Works best with structured CSV-like trade data pasted in.",
    },
    {
        "name": "Client Email Drafter",
        "use_case": "Client Communication",
        "prompt_text": "Draft a professional email to a {{client_type}} client regarding {{topic}}.\n\nKey points to include:\n{{key_points}}\n\nTone: {{tone}}. Length: concise (under 150 words). Sign off as 'The Quantifi Team'.",
        "notes": "Review all client emails before sending. Do not include specific figures without verification.",
    },
    {
        "name": "Risk Report Summarizer v2",
        "use_case": "Risk Summarization",
        "prompt_text": "You are a Chief Risk Officer writing for a board-level audience.\n\nRead the following risk report and write a single 2-sentence executive summary. Focus only on the single most critical finding and the immediate action required. No bullet points — flowing prose only.\n\nReport:\n{{report_text}}",
        "notes": "Compare against Risk Report Summarizer v1 to choose style. v2 is better for board decks, v1 is better for operational teams.",
    },
]


def seed_demo_prompts():
    conn = get_connection()
    existing = conn.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
    if existing == 0:
        for p in DEMO_PROMPTS:
            conn.execute(
                "INSERT INTO prompts (name, use_case, prompt_text, notes) VALUES (?, ?, ?, ?)",
                (p["name"], p["use_case"], p["prompt_text"], p["notes"]),
            )
        conn.commit()
        print(f"Seeded {len(DEMO_PROMPTS)} demo prompts.")
    else:
        print(f"DB already has {existing} prompts — skipping seed.")
    conn.close()


if __name__ == "__main__":
    init_db()
    seed_demo_prompts()
