import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from app.file_processor import (
    extract_text_from_file,
    chunk_text,
    retrieve_relevant_chunks,
)
from app.study_tools import (
    chat_with_notes,
    generate_quiz,
    generate_flashcards,
    generate_mindmap,
    generate_quiz_json,
    generate_flashcards_json,
    generate_mindmap_json,
)
from app.code_analyzer import explain_code, find_bugs, optimize_code

app = FastAPI(title="AI Study & Code Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stored_files = {}


@app.get("/")
def home():
    return {"message": "AI Study & Code Assistant API is running"}


def get_selected_files(file_ids=None):
    if not stored_files:
        return []

    if not file_ids:
        return list(stored_files.values())

    return [
        stored_files[file_id]
        for file_id in file_ids
        if file_id in stored_files
    ]


def get_selected_context(file_ids=None):
    selected_files = get_selected_files(file_ids)

    combined_text = "\n\n".join(
        f"File: {item['filename']}\n{item['text']}"
        for item in selected_files
    )

    return combined_text, selected_files


def get_retrieved_context(question: str, file_ids=None, top_k: int = 5):
    selected_files = get_selected_files(file_ids)

    all_chunks = []

    for item in selected_files:
        for chunk_index, chunk in enumerate(item["chunks"]):
            all_chunks.append(
                {
                    "filename": item["filename"],
                    "folder": item.get("folder", "Default"),
                    "chunk_index": chunk_index + 1,
                    "chunk": chunk,
                }
            )

    chunk_texts = [item["chunk"] for item in all_chunks]

    retrieved_chunks = retrieve_relevant_chunks(
        question=question,
        chunks=chunk_texts,
        top_k=top_k,
    )

    retrieved_context_parts = []
    sources = []

    for index, chunk in enumerate(retrieved_chunks):
        source_item = next(
            (
                item
                for item in all_chunks
                if item["chunk"] == chunk
            ),
            None,
        )

        if source_item:
            source_label = (
                f"{source_item['filename']} "
                f"(chunk {source_item['chunk_index']})"
            )

            sources.append(
                {
                    "filename": source_item["filename"],
                    "folder": source_item["folder"],
                    "chunk_index": source_item["chunk_index"],
                }
            )
        else:
            source_label = f"Unknown source chunk {index + 1}"

        retrieved_context_parts.append(
            f"Relevant Chunk {index + 1} - Source: {source_label}\n{chunk}"
        )

    retrieved_context = "\n\n".join(retrieved_context_parts)

    return {
        "context": retrieved_context,
        "selected_files": selected_files,
        "total_chunks": len(chunk_texts),
        "chunks_used": len(retrieved_chunks),
        "sources": sources,
    }


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Form("Default"),
):
    os.makedirs("uploads", exist_ok=True)

    file_id = str(uuid.uuid4())
    file_path = os.path.join("uploads", f"{file_id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text_from_file(file_path, file.filename)
    chunks = chunk_text(extracted_text)

    stored_files[file_id] = {
        "id": file_id,
        "filename": file.filename,
        "folder": folder,
        "path": file_path,
        "text": extracted_text,
        "chunks": chunks,
    }

    return {
        "file_id": file_id,
        "filename": file.filename,
        "folder": folder,
        "characters": len(extracted_text),
        "chunks": len(chunks),
        "preview": extracted_text[:1000],
    }


@app.post("/upload-multiple")
async def upload_multiple_files(
    files: list[UploadFile] = File(...),
    folder: str = Form("Default"),
):
    uploaded = []

    for file in files:
        os.makedirs("uploads", exist_ok=True)

        file_id = str(uuid.uuid4())
        file_path = os.path.join("uploads", f"{file_id}_{file.filename}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extracted_text = extract_text_from_file(file_path, file.filename)
        chunks = chunk_text(extracted_text)

        stored_files[file_id] = {
            "id": file_id,
            "filename": file.filename,
            "folder": folder,
            "path": file_path,
            "text": extracted_text,
            "chunks": chunks,
        }

        uploaded.append(
            {
                "file_id": file_id,
                "filename": file.filename,
                "folder": folder,
                "characters": len(extracted_text),
                "chunks": len(chunks),
                "preview": extracted_text[:500],
            }
        )

    return {"uploaded": uploaded}


@app.get("/files")
def list_files():
    return {
        "files": [
            {
                "id": item["id"],
                "filename": item["filename"],
                "folder": item["folder"],
                "characters": len(item["text"]),
                "chunks": len(item["chunks"]),
                "preview": item["text"][:500],
            }
            for item in stored_files.values()
        ]
    }


@app.post("/chat")
def chat(payload: dict):
    question = payload.get("question", "")
    file_ids = payload.get("file_ids", [])

    rag_data = get_retrieved_context(
        question=question,
        file_ids=file_ids,
        top_k=5,
    )

    if not rag_data["context"]:
        return {"answer": "Please upload and select at least one file first."}

    answer = chat_with_notes(question, rag_data["context"])

    return {
        "answer": answer,
        "selected_files": len(rag_data["selected_files"]),
        "total_chunks": rag_data["total_chunks"],
        "chunks_used": rag_data["chunks_used"],
        "sources": rag_data["sources"],
        "rag_mode": "lightweight keyword retrieval",
    }


@app.post("/quiz")
def quiz(payload: dict = None):
    payload = payload or {}
    context, selected_files = get_selected_context(payload.get("file_ids", []))

    if not context:
        return {"result": "Please upload and select at least one file first."}

    return {"result": generate_quiz(context)}


@app.post("/flashcards")
def flashcards(payload: dict = None):
    payload = payload or {}
    context, selected_files = get_selected_context(payload.get("file_ids", []))

    if not context:
        return {"result": "Please upload and select at least one file first."}

    return {"result": generate_flashcards(context)}


@app.post("/mindmap")
def mindmap(payload: dict = None):
    payload = payload or {}
    context, selected_files = get_selected_context(payload.get("file_ids", []))

    if not context:
        return {"result": "Please upload and select at least one file first."}

    return {"result": generate_mindmap(context)}


@app.post("/quiz-json")
def quiz_json(payload: dict = None):
    payload = payload or {}
    context, selected_files = get_selected_context(payload.get("file_ids", []))

    if not context:
        return {"error": "Please upload and select at least one file first."}

    total_chunks = sum(len(item["chunks"]) for item in selected_files)

    return {
        "result": generate_quiz_json(context),
        "selected_files": len(selected_files),
        "total_chunks": total_chunks,
        "chunks_used": min(5, total_chunks),
        "rag_mode": "selected document context",
    }


@app.post("/flashcards-json")
def flashcards_json(payload: dict = None):
    payload = payload or {}
    context, selected_files = get_selected_context(payload.get("file_ids", []))

    if not context:
        return {"error": "Please upload and select at least one file first."}

    total_chunks = sum(len(item["chunks"]) for item in selected_files)

    return {
        "result": generate_flashcards_json(context),
        "selected_files": len(selected_files),
        "total_chunks": total_chunks,
        "chunks_used": min(5, total_chunks),
        "rag_mode": "selected document context",
    }


@app.post("/mindmap-json")
def mindmap_json(payload: dict = None):
    payload = payload or {}
    context, selected_files = get_selected_context(payload.get("file_ids", []))

    if not context:
        return {"error": "Please upload and select at least one file first."}

    total_chunks = sum(len(item["chunks"]) for item in selected_files)

    return {
        "result": generate_mindmap_json(context),
        "selected_files": len(selected_files),
        "total_chunks": total_chunks,
        "chunks_used": min(5, total_chunks),
        "rag_mode": "selected document context",
    }


@app.post("/code/explain")
def code_explain(payload: dict):
    code = payload.get("code", "")

    if not code.strip():
        return {"result": "Please paste code first."}

    return {"result": explain_code(code)}


@app.post("/code/bugs")
def code_bugs(payload: dict):
    code = payload.get("code", "")

    if not code.strip():
        return {"result": "Please paste code first."}

    return {"result": find_bugs(code)}


@app.post("/code/optimize")
def code_optimize(payload: dict):
    code = payload.get("code", "")

    if not code.strip():
        return {"result": "Please paste code first."}

    return {"result": optimize_code(code)}