import os
import warnings
from dotenv import load_dotenv

# Suppress Pydantic V1 compatibility warning for Python 3.14
warnings.filterwarnings("ignore", message=".*Core Pydantic V1 functionality isn't compatible.*")

load_dotenv()

# Gemini Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")


def get_llm(force_local: bool = False, prefer_vllm: bool = False):
    """
    Initialize LLM for agent use.
    Uses Google Gemini API.
    """
    return _get_gemini_llm()


def _get_gemini_llm():
    """Get LLM from Google Gemini API."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not set in .env")

    print(f"✅ Using Gemini: {GEMINI_MODEL}")
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.7,
        max_output_tokens=2048,
    )


def get_llm_with_retry():
    """Get LLM via Gemini."""
    return get_llm()
