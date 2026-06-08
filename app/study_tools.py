import json
import re
from app.ai_engine import ask_ai


def extract_json(text: str):
    """
    Safely extracts JSON from the AI response.
    Groq may sometimes return text around the JSON, so this helps clean it.
    """
    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    return None


def chat_with_notes(question: str, context: str) -> str:
    prompt = f"""
You are an AI study assistant. Answer the question using the uploaded notes.

Uploaded notes:
{context[:12000]}

Question:
{question}

Rules:
- Answer clearly.
- Use simple student-friendly language.
- If the answer is not in the notes, say that clearly.
"""
    return ask_ai(prompt)


def generate_quiz(context: str) -> str:
    prompt = f"""
Create 5 multiple-choice quiz questions from these notes.

Notes:
{context[:12000]}

Format:
Q1. Question
A. Option
B. Option
C. Option
D. Option
Answer: Correct option
Explanation: Short explanation
"""
    return ask_ai(prompt)


def generate_flashcards(context: str) -> str:
    prompt = f"""
Create 8 flashcards from these notes.

Notes:
{context[:12000]}

Format:
Front: question or term
Back: answer or explanation
"""
    return ask_ai(prompt)


def generate_mindmap(context: str) -> str:
    prompt = f"""
Create an interactive mind map outline from these notes.

Notes:
{context[:12000]}

Format exactly like this:
Main Topic
- Section 1
  - Detail 1
  - Detail 2
- Section 2
  - Detail 1
  - Detail 2

Keep it clear and organized.
"""
    return ask_ai(prompt)


def generate_quiz_json(context: str):
    prompt = f"""
Create 5 multiple-choice quiz questions from the notes.

Notes:
{context[:12000]}

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations outside JSON.

JSON format:
[
  {{
    "question": "Question text",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "correct_answer": "Exact correct option text",
    "explanation": "Short explanation of why the answer is correct"
  }}
]
"""
    response = ask_ai(prompt)
    data = extract_json(response)

    if data is None:
        return {
            "error": "Could not generate valid quiz JSON.",
            "raw": response
        }

    return data


def generate_flashcards_json(context: str):
    prompt = f"""
Create 8 flashcards from the notes.

Notes:
{context[:12000]}

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations outside JSON.

JSON format:
[
  {{
    "front": "Question or term",
    "back": "Answer or explanation"
  }}
]
"""
    response = ask_ai(prompt)
    data = extract_json(response)

    if data is None:
        return {
            "error": "Could not generate valid flashcard JSON.",
            "raw": response
        }

    return data


def generate_mindmap_json(context: str):
    prompt = f"""
Create a clickable mind map structure from the notes.

Notes:
{context[:12000]}

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations outside JSON.

JSON format:
{{
  "title": "Main Topic",
  "summary": "Short summary of the whole topic",
  "nodes": [
    {{
      "title": "Section title",
      "details": "Explanation of this section",
      "children": [
        {{
          "title": "Subtopic title",
          "details": "Detailed explanation",
          "children": []
        }}
      ]
    }}
  ]
}}
"""
    response = ask_ai(prompt)
    data = extract_json(response)

    if data is None:
        return {
            "error": "Could not generate valid mind map JSON.",
            "raw": response
        }

    return data