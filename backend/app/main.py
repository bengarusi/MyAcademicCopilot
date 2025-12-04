from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware  
from app.schemas import AskRequest, AskResponse
from app.rag import rag_store
from app.rag.loader import DATA_DIR, load_pdf_pages
from app.agents.agents import run_agent
from app.question_routing import classify_question, choose_generation_params, infer_mode
from pathlib import Path



app = FastAPI()

# 👇 להוסיף מיד אחרי יצירת app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # או ["*"] לפיתוח
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/upload-docs")
async def upload_docs(files: list[UploadFile] = File(...)):
    """
    מקבל רשימת קבצים (PDF/TXT), שומר אותם ל-backend/data,
    ומוסיף אותם ל-RAG כך שהבוט ישתמש בהם בשאלות הבאות.
    """
    saved_files: list[str] = []

    for file in files:
        ext = Path(file.filename).suffix.lower()

        if ext not in [".pdf", ".txt"]:
            raise HTTPException(
                status_code=400,
                detail="Only .pdf or .txt files are supported right now.",
            )

        target_path = Path(DATA_DIR) / file.filename

        # שמירת הקובץ לדיסק
        content = await file.read()
        with open(target_path, "wb") as f:
            f.write(content)

        # הוספה ל-RAG
        if ext == ".txt":
            # מפענחים את התוכן ישירות מה-upload
            text = content.decode("utf-8", errors="ignore")
            rag_store.add_document(file.filename, text)

        elif ext == ".pdf":
            # טוענים את ה-PDF לעמודים באמצעות הפונקציה הקיימת שלך
            for doc_id, page_text in load_pdf_pages(str(target_path), file.filename):
                rag_store.add_document(doc_id, page_text)

        saved_files.append(file.filename)

    return {"status": "ok", "files": saved_files}



@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    query = request.query

    # המוח מחליט על המצב (answer / summary / email) לפי הטקסט
    mode = infer_mode(query, request.mode)

    # 🧠 1. סיווג סוג השאלה לפרופיל לוגי
    profile = classify_question(query, mode)

    # 🧠 2. בחירת פרמטרים לפרופיל הזה
    gen_params = choose_generation_params(profile)
    top_k = gen_params["top_k"]
    use_rag = gen_params["use_rag"]
    temperature = gen_params["temperature"]
    max_tokens = gen_params["max_tokens"]

    print(
        f"[routing] mode={mode}, profile={profile}, top_k={top_k}, "
        f"use_rag={use_rag}, temperature={temperature}, max_tokens={max_tokens}"
    )

    # 📚 3. שימוש ב-RAG בהתאם לפרמטרים
    docs = []
    context_chunks: list[str] = []
    citations: list[str] = []
    seen: set[str] = set()

    if use_rag and top_k > 0:
        docs = rag_store.search(query, k=top_k)

        for d in docs:
            # 🧩 מקרה 1: החזרה היא טופל (doc_id, text)
            if isinstance(d, tuple) and len(d) == 2:
                doc_id, text = d

                if text:
                    context_chunks.append(str(text))

                if doc_id and doc_id not in seen:
                    seen.add(str(doc_id))
                    citations.append(str(doc_id))

            else:
                # 🧩 מקרה 2: אובייקט Document עם page_content/metadata
                text = (
                    getattr(d, "page_content", None)
                    or getattr(d, "content", None)
                    or getattr(d, "text", "")
                )
                if text:
                    context_chunks.append(str(text))

                meta = getattr(d, "metadata", None)
                source = None
                page = None

                if isinstance(meta, dict):
                    source = (
                        meta.get("source")
                        or meta.get("file_name")
                        or meta.get("filename")
                        or meta.get("path")
                    )
                    page = (
                        meta.get("page")
                        or meta.get("page_number")
                        or meta.get("slide")
                        or meta.get("page_index")
                    )
                else:
                    source = getattr(d, "source", None)
                    page = getattr(d, "page", None)

                if source:
                    src_name = Path(str(source)).name
                    label = src_name
                    if isinstance(page, int):
                        label = f"{src_name} - שקופית {page + 1}"
                    elif page is not None:
                        label = f"{src_name} - שקופית {page}"

                    if label not in seen:
                        seen.add(label)
                        citations.append(label)

    context_text = "\n\n".join(context_chunks)
      # ⚖️ לוגיקה חדשה: האם באמת השתמשנו במסמכים?

    if not context_text.strip():
        # לא היה קונטקסט מהקבצים -> לא להחזיר רפרנסים בכלל
        citations = []
    else:
        # יש קונטקסט -> להשאיר רק את 3 המקורות הכי חזקים (לפי סדר החיפוש)
        citations = citations[:3]

    # 🤖 4. הפעלת ה-agent עם הקונטקסט והפרמטרים מה"מוח"
    try:
        answer = run_agent(
            mode=mode,
            query=query,
            context_text=context_text,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as e:
        print("ERROR in run_agent:", repr(e))
        answer = None

    # לוג דיבוג – לראות מה באמת חוזר מה-LLM
    print("DEBUG run_agent answer =", repr(answer), "type:", type(answer))

    # ❗ הגנה: לא להחזיר None ל-AskResponse
    if answer is None:
        answer = "לא מצאתי את זה בחומר שהעלת, אנא תדייק את שאלתך"
    elif not isinstance(answer, str):
        # אם ask_llm מחזיר dict/אובייקט אחר – נהפוך למחרוזת
        answer = str(answer)

    # ✅ 5. מחזירים תשובה + רשימת מקורות (citations) לפאנל הימני
    print("CITATIONS RETURNED:", citations)

    return AskResponse(
        mode=mode,
        answer=answer,
        citations=citations,
    )
