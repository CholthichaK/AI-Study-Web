# Library used to read and extract text from PDF files
from pypdf import PdfReader

# Library used to read and extract text from DOCX files
from docx import Document


def extract_text_from_file(file_path: str, filename: str) -> str:
    #    """
    # Detects the file type and extracts text using the correct method.

    # Parameters:
    #     file_path (str):
    #         The saved path of the uploaded file.

    #     filename (str):
    #         The original filename uploaded by the user.

    # Returns:
    #     str:
    #         Extracted text from the file.
    # """

    # Convert filename to lowercase so extension checking is consistent
    filename = filename.lower()

# If the file is a PDF, use PDF extraction
    if filename.endswith(".pdf"):
        return extract_pdf(file_path)

# If the file is a DOCX, use DOCX extraction
    if filename.endswith(".docx"):
        return extract_docx(file_path)

# If the file is plain text or source code, read it as text
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
#    """
#     Extracts text from a PDF file.

#     Parameters:
#         file_path (str):
#             Path to the PDF file.

#     Returns:
#         str:
#             Extracted text from all PDF pages.
#     """


    # Open the PDF file
    reader = PdfReader(file_path)

    # Store extracted text here
    text = ""

    # Loop through every page in the PDF
    for page in reader.pages:
        # Extract text from current page
        page_text = page.extract_text()
        # Add page text only if extraction succeeds
        if page_text:
            text += page_text + "\n"
    # Remove extra spaces/newlines from the final result
    return text.strip()


def extract_docx(file_path: str) -> str:

    #     """
    # Extracts text from a DOCX file.

    # Parameters:
    #     file_path (str):
    #         Path to the DOCX file.

    # Returns:
    #     str:
    #         Extracted paragraph text.
    # """
    
    
    # Open the DOCX document
    doc = Document(file_path)

    # Extract all non-empty paragraphs and join them with new lines
    return "\n".join(
        [
            p.text
            for p in doc.paragraphs
            if p.text.strip()
        ]
    )


def extract_plain_text(file_path: str) -> str:
    #     """
    # Extracts text from TXT and source code files.

    # Parameters:
    #     file_path (str):
    #         Path to the text/code file.

    # Returns:
    #     str:
    #         File contents as text.
    # """


    # Open file using UTF-8 encoding
    # errors="ignore" prevents crashes if unusual characters exist
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
    

    #  """
    # Splits long text into smaller overlapping chunks.

    # This is used for lightweight RAG-style retrieval.

    # Instead of sending an entire document to the AI,
    # the system can search smaller chunks and send only
    # the most relevant parts.

    # Parameters:
    #     text (str):
    #         Full extracted document text.

    #     chunk_size (int):
    #         Maximum number of characters per chunk.

    #     overlap (int):
    #         Number of characters repeated between chunks.
    #         This helps prevent important context from being cut off.

    # Returns:
    #     list:
    #         List of text chunks.
    # """


    """
    Split text into overlapping chunks.

    Example:
    Chunk 1: 0-1200
    Chunk 2: 1050-2250
    Chunk 3: 2100-3300

    This prepares the system for future RAG retrieval.
    """

    # If there is no text, return an empty list
    if not text:
        return []

    # Store generated chunks
    chunks = []

    # Starting character index
    start = 0

    # Continue until the full text has been chunked
    while start < len(text):

        # Calculate where the current chunk should end
        end = start + chunk_size

        # Extract current chunk and remove extra spaces
        chunk = text[start:end].strip()

        # Only add non-empty chunks
        if chunk:
            chunks.append(chunk)

        # Move forward while keeping overlap with previous chunk
        start += chunk_size - overlap

    # Return all chunks
    return chunks


# -----------------------------------------
# Simple Retrieval
# -----------------------------------------

def retrieve_relevant_chunks(
    question: str,
    chunks: list,
    top_k: int = 5,
):
    #     """
    # Retrieves the most relevant chunks using keyword overlap.

    # This is a lightweight retrieval method.
    # It does not use embeddings or FAISS yet.

    # How it works:
    # - Break the user question into words.
    # - Check how many question words appear in each chunk.
    # - Give each chunk a score.
    # - Return the top scoring chunks.

    # Parameters:
    #     question (str):
    #         User's question.

    #     chunks (list):
    #         List of document chunks.

    #     top_k (int):
    #         Number of top chunks to return.

    # Returns:
    #     list:
    #         Most relevant chunks.
    # """

    """
    Lightweight retrieval without embeddings.

    Scores chunks based on keyword overlap.

    Later this can be replaced by:
    - Sentence Transformers
    - FAISS
    - ChromaDB
    """
    # If there are no chunks, return empty list
    if not chunks:
        return []

    # Convert the question into useful lowercase words
    # Short words are ignored because they are often not meaningful
    words = set(
        word.lower()
        for word in question.split()
        if len(word) > 2
    )

    # Store chunk scores
    scored_chunks = []

    # Score each chunk
    for chunk in chunks:

        # Lowercase chunk for easier matching
        chunk_lower = chunk.lower()

        # Score is based on how many question words appear in the chunk
        # Generator Expression
        score = sum(
            1
            for word in words
            if word in chunk_lower
        )

        # Save score with its chunk
        scored_chunks.append(
            (
                score,
                chunk,
            )
        )

    # Sort chunks from highest score to lowest score
    scored_chunks.sort(
        key=lambda x: x[0], #First element of the tuple
        reverse=True, # Decending order
    )

    # Keep only chunks with score greater than 0
    results = [
        chunk
        for score, chunk in scored_chunks[:top_k]
        if score > 0
    ]

    # If no chunks matched the question,
    # return the first few chunks as a fallback
    if not results:
        return chunks[:top_k]

    # Return relevant chunks
    return results


# -----------------------------------------
# RAG Statistics
# -----------------------------------------

def get_chunk_stats(chunks):

    #  """
    # Calculates simple statistics about document chunks.

    # Parameters:
    #     chunks (list):
    #         List of text chunks.

    # Returns:
    #     dict:
    #         Total chunk count and average chunk length.
    # """
     
    return {
        # Number of chunks created from the document
        "total_chunks": len(chunks),

        # Average length of each chunk
        # If there are no chunks, return 0 to avoid division error
        "average_chunk_length": (
            int(
                sum(len(chunk) for chunk in chunks)
                / len(chunks)
            )
            if chunks
            else 0
        ),
    }