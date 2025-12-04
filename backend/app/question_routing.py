# backend/app/question_routing.py
from enum import Enum
from typing import Literal, Dict, Any


# סוגי "פרופילים" של שאלות – אפשר להרחיב בהמשך
class QuestionProfile(str, Enum):
    SHORT_SUMMARY = "short_summary"
    NORMAL_EXPLANATION = "normal_explanation"
    DEEP_EXPLANATION = "deep_explanation"
    BRAINSTORM = "brainstorm"
    CHITCHAT = "chitchat"  # ← חדש: שאלות "מה קורה", "היי", וכו'



def classify_question(query: str, mode: Literal["answer", "summary", "email"]) -> QuestionProfile:
    """מקבל את השאלה וה־mode (answer/summary/email) ומחזיר פרופיל לוגי של השאלה."""
    q = query.lower()

    smalltalk_phrases = [
        "מה קורה",
        "מה המצב",
        "מה נשמע",
        "מה העניינים",
        "היי",
        "שלום",
        "הי",
        "hi",
        "hello",
        "hey",
        "sup",
        "how are you",
    ]
    if any(p in q for p in smalltalk_phrases) and len(q) <= 40:
        return QuestionProfile.CHITCHAT

    # קודם כול – אם המשתמש ביקש סיכום
    if mode == "summary" or "סכם" in q or "summary" in q or "בקצרה" in q:
        return QuestionProfile.NORMAL_EXPLANATION

    # שאלות של "למה / תסביר / שלב אחרי שלב"
    if any(word in q for word in [
        "למה", "תסביר", "explain", "why", "step by step", "שלב אחרי שלב"
    ]):
        return QuestionProfile.DEEP_EXPLANATION

    # רעיונות / בריינסטורמינג
    if any(word in q for word in [
        "רעיונות", "brainstorm", "suggest", "דוגמאות נוספות", "ideas"
    ]):
        return QuestionProfile.BRAINSTORM

    # מיילים – בדרך כלל נוסח, לא רגרסיה ליניארית :)
    if mode == "email":
        return QuestionProfile.NORMAL_EXPLANATION

    # ברירת מחדל
    return QuestionProfile.NORMAL_EXPLANATION


def choose_generation_params(profile: QuestionProfile) -> Dict[str, Any]:
    # תמיד ננסה להשתמש ב-RAG אלא אם בעתיד תוסיף פרופיל "כללי"
    base = {
        "use_rag": True,
        "temperature": 0.2,    # תשובות מדויקות, לא יצירתיות מדי
    }

    
    if profile == QuestionProfile.CHITCHAT:
        # 🔹 small-talk: בלי RAG בכלל, טיפה יותר "חברתי"
        return {
            "use_rag": False,
            "top_k": 0,
            "temperature": 0.7,
            "max_tokens": 120,
        }

    if profile == QuestionProfile.SHORT_SUMMARY:
        return {
            **base,
            "top_k": 4,         # מספיק כדי לתפוס את כל החלקים של הנושא
            "max_tokens": 400,
        }

    if profile == QuestionProfile.DEEP_EXPLANATION:
        return {
            **base,
            "top_k": 8,         # הוכחות + דוגמאות + הגדרות
            "max_tokens": 1200,
        }

    if profile == QuestionProfile.BRAINSTORM:
        return {
            **base,
            "top_k": 6,         # עדיין מבוסס שקפים, אבל טיפה חופש
            "temperature": 0.4, # יותר יצירתיות
            "max_tokens": 800,
        }

    # NORMAL_EXPLANATION
    return {
        **base,
        "top_k": 6,             # הגדרה + אינטואיציה + דוגמה
        "max_tokens": 800,
    }


def infer_mode(
    query: str,
    client_mode: str | None = None,
) -> Literal["answer", "summary", "email"]:
    """
    מזהה לבד אם המשתמש ביקש סיכום / מייל / תשובה רגילה
    לפי הטקסט של השאלה.
    """
    q = query.lower()

    # סימנים לסיכום
    #if any(word in q for word in ["סכם", "סיכום", "summary", "בקצרה", "בנקודות"]):
     #   return "summary"

    # סימנים למייל
    if any(word in q for word in ["מייל", "email", "אמייל", "תנסח מייל", "תכתוב מייל"]):
        return "email"

    # ברירת מחדל – answer
    return client_mode or "answer"