import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load backend/.env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
llm_temperature = 0

def get_llm():
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=llm_temperature,
    )

