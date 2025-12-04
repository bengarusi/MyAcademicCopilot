import os
from typing import List, Tuple
from pypdf import PdfReader

# BASE_DIR = backend/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_pdf_pages(filepath: str, filename: str) -> List[Tuple[str, str]]:
    """
    טוען קובץ PDF ומחזיר רשימת (doc_id, text)
    doc_id = שם הקובץ + מספר עמוד, כדי שנוכל להזכיר אותו ב-citations.
    """
    docs: List[Tuple[str, str]] = []
    reader = PdfReader(filepath)

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if not text:
            continue

        doc_id = f"{filename}_page_{i+1}"
        docs.append((doc_id, text))

    return docs


def load_all_text_files() -> List[Tuple[str, str]]:
    """
    מחזיר רשימת (doc_id, text) עבור כל קובץ בתיקיית data:
    - txt: doc_id = שם הקובץ
    - pdf: doc_id = שם הקובץ + _page_X
    """
    docs: List[Tuple[str, str]] = []

    if not os.path.isdir(DATA_DIR):
        return docs

    for filename in os.listdir(DATA_DIR):
        path = os.path.join(DATA_DIR, filename)

        if filename.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
                docs.append((filename, text))

        elif filename.endswith(".pdf"):
            pdf_docs = load_pdf_pages(path, filename)
            docs.extend(pdf_docs)

    return docs
