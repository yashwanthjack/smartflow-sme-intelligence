# LLM Configuration for SmartFlow Agents
# Supports: vLLM (local), Gemini API, HuggingFace fallback

import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# Track API failures for fallback (Simplified for Local Only)
_MAX_FAILURES_BEFORE_FALLBACK = 0 # Disable Gemini fallback

# vLLM Configuration
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
VLLM_MODEL = os.getenv("VLLM_MODEL", "LiquidAI/LFM2.5-1.2B-Thinking")

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b") # Lightweight default


def get_llm(force_local: bool = True, prefer_vllm: bool = True):
    """
    Initialize LLM for agent use.
    
    Priority:
    1. vLLM local server (OpenAI-compatible)
    2. Ollama (local)
    3. Local HuggingFace model (TinyLlama fallback)
    """
    
    # Priority 1: Try vLLM if configured
    if prefer_vllm:
        try:
            return _get_vllm_llm()
        except Exception as e:
            pass # Try next
    
    # Priority 2: Try Ollama
    try:
        return _get_ollama_llm()
    except Exception as e:
        print(f"⚠️ Ollama not available: {e}")
    
    # Priority 3: Fallback to local HuggingFace model
    print("🔄 Using local HuggingFace LLM fallback (TinyLlama)...")
    return _get_local_llm()


def _get_vllm_llm():
    """Get LLM from local vLLM server."""
    from langchain_openai import ChatOpenAI
    import httpx
    
    try:
        response = httpx.get(f"{VLLM_BASE_URL.replace('/v1', '')}/health", timeout=1.0)
        if response.status_code != 200:
            raise ConnectionError()
    except:
        raise ConnectionError(f"vLLM server not found at {VLLM_BASE_URL}")
    
    print(f"✅ Connected to vLLM: {VLLM_MODEL}")
    return ChatOpenAI(
        model=VLLM_MODEL,
        openai_api_key="none",
        openai_api_base=VLLM_BASE_URL,
        temperature=0.7
    )


def _get_ollama_llm():
    """Get LLM from local Ollama instance."""
    from langchain_community.chat_models import ChatOllama
    import httpx
    
    try:
        httpx.get(OLLAMA_BASE_URL, timeout=1.0)
    except:
        raise ConnectionError(f"Ollama not found at {OLLAMA_BASE_URL}")
        
    print(f"✅ Connected to Ollama: {OLLAMA_MODEL}")
    return ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=0.7
    )


def _get_local_llm():
    """HuggingFace fallback (runs on CPU/GPU directly in process)."""
    # [Same implementation as before, keeping as ultimate fallback]
    try:
        from langchain_huggingface import HuggingFacePipeline
        from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        
        print(f"⚙️  Loading local LLM on {device.upper()}...")
        
        model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        # Fix for "torch_dtype is deprecated" warning
        # Standard API uses torch_dtype, but pipeline/config might complain. 
        # Using 'dtype' as requested if transformers version > 4.26
        model = AutoModelForCausalLM.from_pretrained(model_id, dtype=dtype).to(device)
        
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token_id = tokenizer.eos_token_id
            
        pipe = pipeline(
            "text-generation", model=model, tokenizer=tokenizer, 
            max_new_tokens=512, temperature=0.7, return_full_text=False,
            pad_token_id=tokenizer.pad_token_id,
            repetition_penalty=1.1
        )
        return HuggingFacePipeline(pipeline=pipe)
    except Exception as e:
        print(f"❌ Ultimate fallback failed: {e}")
        raise


def get_llm_with_retry():
    """Get LLM, strictly local."""
    return get_llm(force_local=True)


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

