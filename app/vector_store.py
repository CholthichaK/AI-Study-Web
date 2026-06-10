import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


# Free local embedding model
MODEL_NAME = "all-MiniLM-L6-v2"

# Load embedding model once
embedding_model = SentenceTransformer(MODEL_NAME)

# FAISS index and metadata stored in memory
faiss_index = None
chunk_metadata = []


def create_embeddings(texts: list[str]):
    """
    Converts text chunks into vector embeddings.
    """

    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings.astype("float32")


def rebuild_faiss_index(files: dict):
    """
    Rebuilds FAISS index from all uploaded files.
    """

    global faiss_index, chunk_metadata

    all_chunks = []
    chunk_metadata = []

    for file_id, file_data in files.items():
        for index, chunk in enumerate(file_data["chunks"]):
            all_chunks.append(chunk)

            chunk_metadata.append(
                {
                    "file_id": file_id,
                    "filename": file_data["filename"],
                    "folder": file_data.get("folder", "Default"),
                    "chunk_index": index + 1,
                    "chunk": chunk,
                }
            )

    if not all_chunks:
        faiss_index = None
        return

    embeddings = create_embeddings(all_chunks)

    dimension = embeddings.shape[1]

    faiss_index = faiss.IndexFlatIP(dimension)
    faiss_index.add(embeddings)


def keyword_score(question: str, chunk: str) -> float:
    """
    Calculates keyword overlap score between question and chunk.
    """

    question_words = set(
        word.lower()
        for word in question.split()
        if len(word) > 2
    )

    chunk_lower = chunk.lower()

    if not question_words:
        return 0.0

    matches = sum(
        1
        for word in question_words
        if word in chunk_lower
    )

    return matches / len(question_words)


def search_similar_chunks(
    question: str,
    selected_file_ids: list[str] | None = None,
    top_k: int = 5,
):
    """
    Hybrid retrieval:
    - FAISS semantic similarity
    - Keyword overlap
    """

    if faiss_index is None or not chunk_metadata:
        return {
            "chunks": [],
            "sources": [],
            "total_chunks": 0,
            "chunks_used": 0,
        }

    query_embedding = create_embeddings([question])

    # Retrieve more candidates than needed
    scores, indices = faiss_index.search(query_embedding, top_k * 6)

    selected_set = set(selected_file_ids or [])

    candidates = []

    for semantic_score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(chunk_metadata):
            continue

        item = chunk_metadata[idx]

        if selected_set and item["file_id"] not in selected_set:
            continue

        key_score = keyword_score(question, item["chunk"])

        final_score = (0.75 * float(semantic_score)) + (0.25 * key_score)

        candidates.append(
            {
                "chunk": item["chunk"],
                "filename": item["filename"],
                "folder": item["folder"],
                "chunk_index": item["chunk_index"],
                "semantic_score": float(semantic_score),
                "keyword_score": key_score,
                "final_score": final_score,
            }
        )

    candidates.sort(
        key=lambda x: x["final_score"],
        reverse=True,
    )

    top_results = candidates[:top_k]

    results = [
        item["chunk"]
        for item in top_results
    ]

    sources = [
        {
            "filename": item["filename"],
            "folder": item["folder"],
            "chunk_index": item["chunk_index"],
            "semantic_score": round(item["semantic_score"], 3),
            "keyword_score": round(item["keyword_score"], 3),
            "final_score": round(item["final_score"], 3),
        }
        for item in top_results
    ]

    return {
        "chunks": results,
        "sources": sources,
        "total_chunks": len(chunk_metadata),
        "chunks_used": len(results),
    }