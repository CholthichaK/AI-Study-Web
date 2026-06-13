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


def generate_quiz_json(
    context: str,
    previous_questions=None,
):

    previous_questions = previous_questions or []

    previous_text = "\n".join(
        f"- {question}"
        for question in previous_questions
    )

    prompt = f"""
Create 5 multiple-choice quiz questions from the notes.

Previously generated questions:

{previous_text if previous_text else "None"}

Requirements:

- Do NOT repeat any previous questions.
- Do NOT create reworded versions of previous questions.
- Generate completely new questions.
- Focus on different concepts from the notes.
- Cover different sections of the material.
- Mix easy, medium, and difficult questions.
- Prefer application-based questions.

Notes:
{context[:12000]}

Return ONLY valid JSON.
...
"""


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

def generate_flashcards_json(
    context: str,
    previous_flashcards=None,
):
    """
    Generate study-focused flashcards.

    When users click "Generate Another Set",
    previously generated flashcards are provided
    so the AI can avoid repetition.
    """

    previous_flashcards = previous_flashcards or []

    previous_text = "\n".join(
        f"- {card}"
        for card in previous_flashcards
    )

    prompt = f"""
You are an expert educator and learning designer.

Create 8 high-quality flashcards from the notes.

Notes:
{context[:12000]}

Previously generated flashcards:

{previous_text if previous_text else "None"}

Requirements:

- Do NOT repeat previous flashcards.
- Do NOT create reworded versions of previous flashcards.
- Generate completely new flashcards.
- Focus on concepts not previously covered.
- Cover different sections of the notes.
- Prioritize important learning material.
- Mix different flashcard styles.

Include a combination of:

- Definitions
- Examples
- Relationships between concepts
- Real-world applications
- Exam-relevant concepts
- Common mistakes and misconceptions

Good flashcards should help students:

- Understand
- Memorize
- Apply
- Revise

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
            "raw": response,
        }

    return data

def generate_mindmap_json(
    context: str,
    previous_mindmaps=None,
):
    """
    Generates a study-focused structured JSON mind map.

    Designed to:
    - Improve understanding
    - Improve revision
    - Show relationships between concepts
    - Avoid repeating previous mind maps
    """

    previous_mindmaps = previous_mindmaps or []

    previous_text = "\n".join(
        f"- {item}"
        for item in previous_mindmaps
    )

    prompt = f"""
You are an expert educator, learning scientist, and curriculum designer.

Your task is to transform the notes into a study-focused mind map that helps a student:

- Understand the topic quickly
- Remember important concepts
- See relationships between ideas
- Prepare for quizzes and exams
- Review the material efficiently

Notes:
{context[:12000]}

Previously generated mind map branches:
{previous_text if previous_text else "None"}

Instructions regarding previous mind maps:

- Avoid repeating the exact same branch names when possible.
- Avoid repeating the exact same hierarchy.
- Prefer concepts that were previously underexplored.
- If major concepts were already covered, create deeper branches rather than repeating them.
- The goal is to provide a fresh learning perspective while remaining useful for studying.

Learning Priorities (highest importance first):

1. Core Concepts
2. Relationships Between Concepts
3. Important Definitions
4. Examples and Applications
5. Exam-Relevant Points
6. Common Mistakes and Misconceptions

Mind Map Design Rules:

- Create ONE central topic.
- Create 4–6 major branches.
- Each major branch should represent an important learning area.
- Each major branch should contain 2–4 meaningful child nodes.
- Child nodes should explain:
  - definitions
  - examples
  - relationships
  - applications
  - exam tips
  - common mistakes

Do NOT:

- Create branches for UI actions.
- Create branches for button clicks or software steps.
- Create vague labels.
- Create duplicate concepts.
- Create branches containing only one word with no meaning.
- Repeat the same idea under multiple branches.

Branch Naming Rules:

Bad Examples:
- Stuff
- More Details
- Process
- Information

Good Examples:
- Object-Oriented Programming Principles
- Database Relationships
- Neural Network Training Process
- Classification Evaluation Metrics
- Causes of Customer Churn

The resulting mind map should feel like a high-quality study guide created by a professor.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations outside JSON.

JSON format:

{{
  "title": "Main Topic",
  "summary": "2-3 sentence overview of the topic",
  "nodes": [
    {{
      "title": "Major Study Branch",
      "details": "Why this branch matters",
      "children": [
        {{
          "title": "Important Concept",
          "details": "Explanation, example, relationship, or exam note",
          "children": []
        }},
        {{
          "title": "Important Concept",
          "details": "Explanation, example, relationship, or exam note",
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
            "raw": response,
        }

    return data