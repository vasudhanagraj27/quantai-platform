import time
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_MSG = (
    "You are a helpful AI assistant for Quantifi, a financial risk management firm. "
    "Answer clearly and professionally."
)


def run_prompt(rendered_prompt: str, api_key: str, model: str = GROQ_MODEL) -> tuple[str, int]:
    llm = ChatGroq(api_key=api_key, model=model, temperature=0.2, max_tokens=1024)
    messages = [SystemMessage(content=SYSTEM_MSG), HumanMessage(content=rendered_prompt)]
    start = time.time()
    response = llm.invoke(messages)
    latency_ms = int((time.time() - start) * 1000)
    return response.content, latency_ms


def run_comparison(
    prompt_a: str,
    prompt_b: str,
    api_key: str,
    model: str = GROQ_MODEL,
) -> tuple[str, int, str, int]:
    output_a, lat_a = run_prompt(prompt_a, api_key, model)
    output_b, lat_b = run_prompt(prompt_b, api_key, model)
    return output_a, lat_a, output_b, lat_b


def judge_outputs(
    name_a: str,
    output_a: str,
    name_b: str,
    output_b: str,
    api_key: str,
    model: str = GROQ_MODEL,
) -> str:
    llm = ChatGroq(api_key=api_key, model=model, temperature=0.1, max_tokens=400)
    judge_prompt = f"""You are an expert AI prompt evaluator for a financial risk management firm.

Compare these two AI-generated outputs and declare a winner.

--- OUTPUT A ({name_a}) ---
{output_a}

--- OUTPUT B ({name_b}) ---
{output_b}

Evaluate on: clarity, accuracy, professionalism, and usefulness for a financial team.

Respond in this exact format:
🏆 WINNER: [A or B] — [one sentence reason]

STRENGTHS:
• A: [one strength]
• B: [one strength]

WEAKNESSES:
• A: [one weakness]
• B: [one weakness]

VERDICT: [one sentence on when to use A vs when to use B]"""

    response = llm.invoke([HumanMessage(content=judge_prompt)])
    return response.content.strip()
