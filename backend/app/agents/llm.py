# LLM Configuration for SmartFlow Agents
# Supports: vLLM (local), Gemini API, HuggingFace fallback

import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# Track API failures for fallback
_gemini_failures = 0
_MAX_FAILURES_BEFORE_FALLBACK = 2

# vLLM Configuration
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
VLLM_MODEL = os.getenv("VLLM_MODEL", "LiquidAI/LFM2.5-1.2B-Thinking")


def get_llm(force_local: bool = False, prefer_vllm: bool = True):
    """
    Initialize LLM for agent use.
    
    Priority:
    1. vLLM local server (if prefer_vllm=True and server is running)
    2. Gemini API (if available and not rate-limited)
    3. Local HuggingFace model (TinyLlama fallback)
    
    Args:
        force_local: Force use of local model even if Gemini is available
        prefer_vllm: Prefer vLLM local server over cloud APIs
    """
    global _gemini_failures
    
    # Priority 1: Try vLLM if preferred
    if prefer_vllm:
        try:
            return _get_vllm_llm()
        except Exception as e:
            print(f"⚠️ vLLM not available: {e}")
    
    # Priority 2: Try Gemini if not forcing local
    if not force_local and _gemini_failures < _MAX_FAILURES_BEFORE_FALLBACK:
        try:
            return _get_gemini_llm()
        except Exception as e:
            print(f"⚠️ Gemini failed: {e}")
            _gemini_failures += 1
    
    # Priority 3: Fallback to local HuggingFace model
    print("🔄 Using local HuggingFace LLM fallback...")
    return _get_local_llm()


def _get_vllm_llm():
    """
    Get LLM from vLLM server using OpenAI-compatible API.
    
    Requires vLLM server running:
        pip install vllm
        vllm serve "LiquidAI/LFM2.5-1.2B-Thinking"
    """
    from langchain_openai import ChatOpenAI
    import httpx
    
    # Quick health check
    try:
        response = httpx.get(f"{VLLM_BASE_URL.replace('/v1', '')}/health", timeout=2.0)
        if response.status_code != 200:
            raise ConnectionError("vLLM server not responding")
    except httpx.RequestError:
        raise ConnectionError(f"Cannot connect to vLLM at {VLLM_BASE_URL}")
    
    print(f"✅ Connected to vLLM server: {VLLM_MODEL}")
    
    return ChatOpenAI(
        model=VLLM_MODEL,
        openai_api_key="not-needed",  # vLLM doesn't require API key
        openai_api_base=VLLM_BASE_URL,
        temperature=0.7,
        max_tokens=1024,
    )


def _get_gemini_llm():
    """Get Gemini LLM instance."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key=api_key,
        temperature=0.7,
        convert_system_message_to_human=True
    )


def _get_local_llm():
    """
    Get local LLM using HuggingFace transformers.
    Uses a small model that can run on CPU.
    """
    try:
        from langchain_huggingface import HuggingFacePipeline
        from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
        import torch
        
        # Use a small, efficient model
        model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        
        print(f"📥 Loading local model: {model_id}")
        
        # Check for GPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=dtype,
            device_map="auto" if device == "cuda" else None
        )
        
        if device == "cpu":
            model = model.to("cpu")
        
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id
        )
        
        llm = HuggingFacePipeline(pipeline=pipe)
        print("✅ Local model loaded successfully")
        return llm
        
    except ImportError:
        print("❌ HuggingFace not installed. Install with: pip install transformers torch langchain-huggingface")
        raise
    except Exception as e:
        print(f"❌ Failed to load local model: {e}")
        raise


def reset_gemini_failures():
    """Reset the failure counter to retry Gemini."""
    global _gemini_failures
    _gemini_failures = 0


def get_llm_with_retry():
    """
    Get LLM with automatic retry on rate limit errors.
    Catches RESOURCE_EXHAUSTED and switches to local model.
    """
    try:
        llm = get_llm(force_local=False)
        return llm
    except Exception as e:
        error_str = str(e)
        if "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
            print("⚠️ Gemini quota exhausted, switching to local model")
            return get_llm(force_local=True)
        raise


def check_vllm_status() -> dict:
    """Check if vLLM server is running and return status."""
    import httpx
    
    try:
        response = httpx.get(f"{VLLM_BASE_URL.replace('/v1', '')}/health", timeout=2.0)
        return {
            "available": response.status_code == 200,
            "url": VLLM_BASE_URL,
            "model": VLLM_MODEL
        }
    except Exception:
        return {
            "available": False,
            "url": VLLM_BASE_URL,
            "model": VLLM_MODEL
        }

