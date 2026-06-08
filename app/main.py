import os
import shutil
import uuid

# FastAPI tools for creating API routes and handling file uploads
from fastapi import FastAPI, UploadFile, File, Form

# Middleware that allows the frontend to communicate with the backend
from fastapi.middleware.cors import CORSMiddleware


# File processing functions
from app.file_processor import (
    extract_text_from_file,
    chunk_text,
    retrieve_relevant_chunks,
)

# Study assistant functions
from app.study_tools import (
    chat_with_notes,
    generate_quiz,
    generate_flashcards,
    generate_mindmap,
    generate_quiz_json,
    generate_flashcards_json,
    generate_mindmap_json,
)

# Code analysis functions
from app.code_analyzer import explain_code, find_bugs, optimize_code


# Create the FastAPI application
app = FastAPI(title="AI Study & Code Assistant API")


# Allow requests from the Streamlit frontend
# This is useful when frontend and backend run on different ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all request headers
)


# In-memory file storage
# Uploaded files are stored here while the backend is running
# Note: This resets when the server restarts
stored_files = {}


@app.get("/")
def home():

    #  """
    # Root endpoint used to check if the API is running.

    # Returns:
    #     dict:
    #         Simple status message.
    # """
    return {"message": "AI Study & Code Assistant API is running"}


def get_selected_files(file_ids=None):

    #  """
    # Gets selected files from memory.

    # If no file IDs are provided, all uploaded files are selected.

    # Parameters:
    #     file_ids (list | None):
    #         List of selected file IDs from the frontend.

    # Returns:
    #     list:
    #         Selected file objects.
    # """

    # If no files are uploaded, return empty list
    if not stored_files:
        return []

    # If frontend sends no selected IDs, use all files
    if not file_ids:
        return list(stored_files.values())

    # Return only files whose IDs match selected IDs
    return [
        stored_files[file_id]
        for file_id in file_ids
        if file_id in stored_files
    ]


def get_selected_context(file_ids=None):

    #   """
    # Combines full text from selected files.

    # This is used for tools such as quiz, flashcards,
    # and mind map generation.

    # Parameters:
    #     file_ids (list | None):
    #         Selected file IDs.

    # Returns:
    #     tuple:
    #         combined_text (str), selected_files (list)
    # """


     # Get selected file objects
    selected_files = get_selected_files(file_ids)

    # Combine selected file texts into one large context
    combined_text = "\n\n".join(
        f"File: {item['filename']}\n{item['text']}"
        for item in selected_files
    )

    #blank lines between files

    return combined_text, selected_files


def get_retrieved_context(question: str, file_ids=None, top_k: int = 5):
    #    """
    # Retrieves relevant chunks from selected files.

    # This is the lightweight RAG-style retrieval step.

    # Flow:
    # 1. Get selected files.
    # 2. Collect all chunks from those files.
    # 3. Score chunks based on keyword overlap.
    # 4. Retrieve top_k most relevant chunks.
    # 5. Build a context string for the AI.

    # Parameters:
    #     question (str):
    #         User's question.

    #     file_ids (list | None):
    #         Selected file IDs.

    #     top_k (int):
    #         Number of chunks to retrieve.

    # Returns:
    #     dict:
    #         Retrieved context, selected files, chunk stats, and sources.
    # """
    
    selected_files = get_selected_files(file_ids)

    # Store all chunks with metadata
    all_chunks = []

    # Loop through selected files
    for item in selected_files:

        # Loop through each chunk in the file
        for chunk_index, chunk in enumerate(item["chunks"]):

            # Store chunk text plus source information
            all_chunks.append(
                {
                    "filename": item["filename"],
                    "folder": item.get("folder", "Default"),
                    "chunk_index": chunk_index + 1,
                    "chunk": chunk,
                }
            )

    # Extract only the chunk text for retrieval scoring
    chunk_texts = [item["chunk"] for item in all_chunks]

    # Retrieve the most relevant chunks using lightweight keyword matching
    retrieved_chunks = retrieve_relevant_chunks(
        question=question,
        chunks=chunk_texts,
        top_k=top_k,
    )

    # These will be sent to the AI as context
    retrieved_context_parts = []

    # These will be returned to the frontend as source information
    sources = []

    # Loop through retrieved chunks and match each chunk back to its source file
    for index, chunk in enumerate(retrieved_chunks):
       # Find the original file/chunk metadata
        source_item = next(
            (
                item
                for item in all_chunks
                if item["chunk"] == chunk
            ),
            None,
        )

        # If source metadata is found, create source label
        if source_item:
            source_label = (
                f"{source_item['filename']} "
                f"(chunk {source_item['chunk_index']})"
            )

            # Store source info for frontend display
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