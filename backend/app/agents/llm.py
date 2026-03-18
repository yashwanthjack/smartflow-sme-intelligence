import os
import warnings
from dotenv import load_dotenv

# Suppress Pydantic V1 compatibility warning for Python 3.14
warnings.filterwarnings("ignore", message=".*Core Pydantic V1 functionality isn't compatible.*")

load_dotenv()

# Groq Configuration (Free API)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

def get_llm(force_local: bool = False, prefer_vllm: bool = False):
    """
    Initialize LLM for agent use.
    Uses Groq API (free tier available).
    """
    return _get_groq_llm()

def _get_groq_llm():
    """Get LLM from Groq API."""
    from langchain_groq import ChatGroq

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set in .env")

    print(f"✅ Using Groq: {GROQ_MODEL}")
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=0.7,
        max_tokens=2048
    )

def get_llm_with_retry():
    """Get LLM via Groq."""
    return get_llm()
