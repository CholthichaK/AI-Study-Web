
# Import OS so we can read environment variables
import os

# Load variables from .env file
from dotenv import load_dotenv

# Official Groq Python SDK
from groq import Groq

# Load .env file into environment variables
load_dotenv()


# Create Groq client using API key from .env
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# Default model to use
# If GROQ_MODEL exists in .env it will use that
# Otherwise it falls back to llama-3.1-8b-instant
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


# Check if API key exists
def ask_ai(prompt: str, system: str = "You are a helpful AI study and coding assistant.") -> str:
    if not os.getenv("GROQ_API_KEY"):
        return "Error: GROQ_API_KEY is missing. Add it to your .env file."
    
    # """
    # Sends a prompt to Groq and returns the AI response.

    # Parameters:
    #     prompt (str):
    #         The user's question or task.

    #     system (str):
    #         System instructions that define the AI's behavior.

    # Returns:
    #     str:
    #         The AI-generated response.
    # """


    # Send request to Groq model
    response = client.chat.completions.create(

         # AI model to use
        model=MODEL,

        # Conversation messages
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],

        # Lower temperature = more accurate and consistent
        # Higher temperature = more creative
        temperature=0.3,
    
        # Maximum length of generated response
        max_tokens=1200,
    )
    # Return the AI's reply text
    return response.choices[0].message.content