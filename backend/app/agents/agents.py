from app.llm.client import ask_llm


def build_instruction_for_mode(mode: str) -> str:
    """
    מחזיר הנחיית מערכת (instruction) לפי מצב הפעולה.
    זה בעצם המוח של ה"Agent".
    """
    if mode == "answer":
        return (
            "ענה בעברית, בצורה ברורה וקצרה, "
            "ב-2–4 משפטים. אתה יכול להשתמש גם בידע כללי וגם בקונטקסט."
        )
    elif mode == "email":
        return (
            "כתוב מייל קצר בעברית, מקצועי וידידותי, על בסיס השאלה והקונטקסט. "
            "אל תוסיף כותרות או נמען, רק את גוף המייל עצמו."
        )
    elif mode == "summary":
        return (
            "סכם את המידע הרלוונטי בעברית ב-3–5 נקודות קצרות. "
            "אפשר להשתמש ברשימה עם כוכביות או מקפים אם זה עוזר לקריאות."
        )
    else:
        return "ענה בעברית בצורה ברורה וקצרה."


def run_agent(
    mode: str,
    query: str,
    context_text: str,
    temperature: float = 0.2,
    max_tokens: int = 800,
) -> str:
    """
    Agent כללי:
    - בוחר instruction לפי mode
    - בונה prompt עם הקונטקסט
    - קורא ל-LLM דרך ask_llm עם הפרמטרים שה"מוח" בחר
    """
    instruction = build_instruction_for_mode(mode)

    prompt = f"""
You are an AI copilot.

Instruction:
{instruction}

Use the following context if it is relevant. Prefer the context over your own knowledge
when there is a conflict.

Context:
{context_text}

User question (mode={mode}):
{query}
"""

    answer = ask_llm(
        prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return answer
