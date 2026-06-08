import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def ask_ai(prompt: str, system: str = "You are a helpful AI study and coding assistant.") -> str:
    if not os.getenv("GROQ_API_KEY"):
        return "Error: GROQ_API_KEY is missing. Add it to your .env file."

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=1200,
    )

    return response.choices[0].message.content