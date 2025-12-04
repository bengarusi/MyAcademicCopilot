import os
from dotenv import load_dotenv
import litellm

# 👇 זה הייבוא החדש הנכון ל-SDK v3
from langfuse import observe


load_dotenv()

# ----- Gemini API Key -----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing in .env")

# LiteLLM מחפש את המפתח במשתנה סביבה
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

# ----- Langfuse keys -----
# מספיק שהגדרת אותם ב-.env:
# LANGFUSE_SECRET_KEY=sk-lf-...
# LANGFUSE_PUBLIC_KEY=pk-lf-...
# LANGFUSE_BASE_URL=https://cloud.langfuse.com
# ה-SDK קורא אותם לבד, לא צריך ליצור client ידנית.

DEFAULT_MODEL = "gemini/gemini-2.5-flash"


@observe(name="llm_generation")
def ask_llm(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.2,
    max_tokens: int | None = None,
) -> str:
    """
    פניה ל-LLM דרך LiteLLM + תיעוד ב-Langfuse,
    עם תמיכה ב-temperature ו-max_tokens כדי שה"מוח" ישלוט בסגנון התשובה.
    """
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response["choices"][0]["message"]["content"]
