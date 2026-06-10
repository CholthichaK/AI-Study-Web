import json # Used for converting JSON strings into Python objects
import re # Used for searching text with patterns (Regular Expressions)
from app.ai_engine import ask_ai # Our Groq AI wrapper function

#function receives a string called text
def extract_json(text: str):
    """
    Safely extracts JSON from the AI response.
    Groq may sometimes return text around the JSON, so this helps clean it.
    """
    try:
        # Directly load the JSON string
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


def chat_with_notes(
    question: str,
    context: str,
    chat_memory: str = "",
) -> str:
    prompt = f"""
You are an AI study assistant.

You can answer using:
1. Retrieved uploaded notes
2. Previous conversation history

Retrieved Notes:
{context[:12000]}

Conversation History:
{chat_memory}

Current Question:
{question}

Rules:
- If the answer is in the conversation history, use the conversation history.
- If the answer is in the uploaded notes, use the uploaded notes.
- If the user asks about something they mentioned earlier, remember it from conversation history.
- For personal details, deadlines, due dates, tasks, or plans mentioned by the user, trust the conversation history.
- Do not say "not in the uploaded notes" if the answer is available in the conversation history.
- If the answer is not in either the notes or conversation history, say you do not have that information.
- Answer clearly and naturally.
"""

    return ask_ai(prompt)


def generate_quiz(context: str) -> str:
    prompt = f"""
Create 5 multiple-choice quiz questions from these notes.

Previously generated questions:

{previous_text}

Requirements:

- Do NOT repeat any previous questions.
- Do NOT create reworded versions of previous questions.
- Generate completely new questions.
- Focus on different concepts from the notes.
- Cover different sections of the material.
- Mix easy, medium, and difficult questions.

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


def generate_quiz_json(
    context: str,
    previous_questions=None,
):
    previous_questions = previous_questions or []
    previous_text = "\n".join(
    f"- {q}"
    for q in previous_questions
)
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
    """
    Generates a study-focused structured JSON mind map.

    This version is designed to create meaningful learning nodes,
    not random tiny actions or unclear branches.
    """

    prompt = f"""
You are an expert learning designer.

Create a study-focused mind map from the notes.

Notes:
{context[:12000]}

Your goal:
- Help a student understand and revise the topic.
- Focus on concepts, definitions, relationships, examples, and exam points.
- Do NOT create nodes for small actions like "click", "type", "press enter", or UI steps.
- Do NOT create random procedural steps unless the notes are clearly about a process.
- Keep the map clean and useful for studying.

Mind map rules:
- Create 1 main topic.
- Create 4 to 6 main branches.
- Each main branch should have 2 to 4 child nodes.
- Each node should contain useful study details.
- Details should explain meaning, importance, or examples.
- Use clear academic labels.
- Avoid duplicate nodes.
- Avoid very short unclear labels.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations outside JSON.

JSON format:
{{
  "title": "Main Study Topic",
  "summary": "A short overview of the topic in 2-3 sentences.",
  "nodes": [
    {{
      "title": "Core Concept",
      "details": "Explain what this branch means and why it matters.",
      "children": [
        {{
          "title": "Definition",
          "details": "Clear definition based on the notes.",
          "children": []
        }},
        {{
          "title": "Example",
          "details": "A useful example based on the notes.",
          "children": []
        }}
      ]
    }},
    {{
      "title": "Important Process",
      "details": "Explain the process or relationship if relevant.",
      "children": [
        {{
          "title": "Step or Component",
          "details": "Explain this part clearly.",
          "children": []
        }}
      ]
    }},
    {{
      "title": "Key Terms",
      "details": "Important vocabulary students should remember.",
      "children": [
        {{
          "title": "Term",
          "details": "Meaning of the term.",
          "children": []
        }}
      ]
    }},
    {{
      "title": "Exam Notes",
      "details": "Important points likely to be tested.",
      "children": [
        {{
          "title": "Common Question",
          "details": "Explain what students should know.",
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