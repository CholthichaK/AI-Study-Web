from pypdf import PdfReader
from docx import Document


def extract_text_from_file(file_path: str, filename: str) -> str:
    filename = filename.lower()

    if filename.endswith(".pdf"):
        return extract_pdf(file_path)

    if filename.endswith(".docx"):
        return extract_docx(file_path)

    if filename.endswith(
        (
            ".txt",
            ".py",
            ".java",
            ".js",
            ".cpp",
            ".html",
            ".css",
        )
    ):
        return extract_plain_text(file_path)

    return "Unsupported file type."


def extract_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()


def extract_docx(file_path: str) -> str:
    doc = Document(file_path)

    return "\n".join(
        [
            p.text
            for p in doc.paragraphs
            if p.text.strip()
        ]
    )


def extract_plain_text(file_path: str) -> str:
    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as file:
        return file.read()


# -----------------------------------------
# Lightweight RAG Chunking
# -----------------------------------------

def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 150,
):
    """
    Split text into overlapping chunks.

    Example:
    Chunk 1: 0-1200
    Chunk 2: 1050-2250
    Chunk 3: 2100-3300

    This prepares the system for future RAG retrieval.
    """

    if not text:
        return []

    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# -----------------------------------------
# Simple Retrieval
# -----------------------------------------

def retrieve_relevant_chunks(
    question: str,
    chunks: list,
    top_k: int = 5,
):
    """
    Lightweight retrieval without embeddings.

    Scores chunks based on keyword overlap.

    Later this can be replaced by:
    - Sentence Transformers
    - FAISS
    - ChromaDB
    """

    if not chunks:
        return []

    words = set(
        word.lower()
        for word in question.split()
        if len(word) > 2
    )

    scored_chunks = []

    for chunk in chunks:
        chunk_lower = chunk.lower()

        score = sum(
            1
            for word in words
            if word in chunk_lower
        )

        scored_chunks.append(
            (
                score,
                chunk,
            )
        )

    scored_chunks.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    results = [
        chunk
        for score, chunk in scored_chunks[:top_k]
        if score > 0
    ]

    if not results:
        return chunks[:top_k]

    return results


# -----------------------------------------
# RAG Statistics
# -----------------------------------------

def get_chunk_stats(chunks):
    return {
        "total_chunks": len(chunks),
        "average_chunk_length": (
            int(
                sum(len(chunk) for chunk in chunks)
                / len(chunks)
            )
            if chunks
            else 0
        ),
    }