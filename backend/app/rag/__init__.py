import os
import json
from typing import Dict, Any
from .store import SimpleRAGStore
from .loader import load_all_text_files, DATA_DIR  # DATA_DIR מוגדר ב-loader.py

# קבצי cache בתוך תיקיית data
CACHE_PATH = os.path.join(DATA_DIR, "rag_cache.npz")
META_PATH = os.path.join(DATA_DIR, "rag_cache_meta.json")


def build_data_signature() -> Dict[str, Any]:
    """
    מחזיר "חתימה" על תיקיית data:
    לכל קובץ רלוונטי (pdf/txt) שומרים:
    - גודל (bytes)
    - זמן שינוי אחרון (mtime)
    """
    sig: Dict[str, Any] = {}
    for filename in os.listdir(DATA_DIR):
        if not (filename.endswith(".pdf") or filename.endswith(".txt")):
            continue
        path = os.path.join(DATA_DIR, filename)
        if not os.path.isfile(path):
            continue
        stat = os.stat(path)
        sig[filename] = {
            "size": stat.st_size,
            "mtime": stat.st_mtime,  # float, שניות מאז epoch
        }
    return sig


def load_previous_signature() -> Dict[str, Any]:
    if not os.path.exists(META_PATH):
        return {}
    try:
        with open(META_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # אם הקובץ הרוס/לא קריא – נתייחס כאילו אין cache
        return {}


def save_signature(sig: Dict[str, Any]) -> None:
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(sig, f)


# --- לוגיקת האתחול של ה-RAG ---

current_sig = build_data_signature()
prev_sig = load_previous_signature()

use_cache = os.path.exists(CACHE_PATH) and (current_sig == prev_sig)

if use_cache:
    # 👇 אין שינוי בקבצים – טוענים cache
    rag_store = SimpleRAGStore.load_cache(CACHE_PATH)
    print(f"[RAG] Loaded {len(rag_store.docs)} documents from cache")
else:
    # 👇 יש שינוי (או אין cache) – בונים מחדש
    print("[RAG] Building embeddings from data directory...")
    docs = load_all_text_files()
    rag_store = SimpleRAGStore()

    for doc_id, text in docs:
        rag_store.add_document(doc_id, text)

    # שמירת cache + חתימה
    rag_store.save_cache(CACHE_PATH)
    save_signature(current_sig)
    print(f"[RAG] Loaded {len(docs)} documents into memory and saved cache")
