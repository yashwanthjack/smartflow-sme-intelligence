import os
import warnings
from dotenv import load_dotenv
from typing import Optional

# Suppress Pydantic V1 compatibility warning for Python 3.14
warnings.filterwarnings("ignore", message=".*Core Pydantic V1 functionality isn't compatible.*")

load_dotenv()

# Track API failures for fallback (Simplified for Local Only)
_MAX_FAILURES_BEFORE_FALLBACK = 0 # Disable Gemini fallback

# vLLM Configuration
# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b") # User selected Qwen 8B

# Hugging Face Inference API Configuration
HF_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")

def get_llm(force_local: bool = True, prefer_vllm: bool = True):
    """
    Initialize LLM for agent use.
    
    Priority:
    1. Ollama (Local - Preferred)
    2. Hugging Face Inference API (Cloud - Fallback)
    3. vLLM local server
    4. Local HuggingFace model (TinyLlama fallback)
    """

    # Priority 1: Try Ollama (Local)
    try:
        return _get_ollama_llm()
    except Exception as e:
        # print(f"⚠️ Ollama not available: {e}")
        pass

    # Priority 2: Try Hugging Face Inference API
    if HF_API_TOKEN:
        try:
            return _get_huggingface_llm()
        except Exception as e:
            print(f"⚠️ Hugging Face API failed: {e}")
            
    # Priority 3: Try vLLM if configured
    if prefer_vllm:
        try:
            return _get_vllm_llm()
        except Exception as e:
            pass # Try next
        
    # Priority 4: Fallback to local HuggingFace model
    print("🔄 Using local HuggingFace LLM fallback (TinyLlama)...")
    return _get_local_llm()

def _get_huggingface_llm():
    """Get LLM from Hugging Face Inference API."""
    from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
    
    print(f"✅ Connected to Hugging Face API: {HF_MODEL_NAME}")
    llm = HuggingFaceEndpoint(
        repo_id=HF_MODEL_NAME,
        # task="conversational", # LangChain might not support this task string directly in Endpoint validation
        max_new_tokens=512,
        top_k=50,
        temperature=0.7,
        huggingfacehub_api_token=HF_API_TOKEN
    )
    return ChatHuggingFace(llm=llm)


def _get_vllm_llm():
    """Get LLM from local vLLM server."""
    from langchain_openai import ChatOpenAI
    import httpx
    
    try:
        # Check /v1/models to ensure it's actually an LLM server, not just our backend's /health
        response = httpx.get(f"{VLLM_BASE_URL}/models", timeout=1.0)
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
    try:
        from langchain_ollama import ChatOllama
    except ImportError:
        from langchain_community.chat_models import ChatOllama
    import httpx
    
    try:
        httpx.get(OLLAMA_BASE_URL, timeout=1.0)
    except:
        # Don't raise error, let LangChain try or fail gracefully, or just warn.
        # But keeping original logic is safer for now, just updated import.
        # Actually original logic raised ConnectionError.
        raise ConnectionError(f"Ollama not found at {OLLAMA_BASE_URL}")
        
    print(f"✅ Connected to Ollama: {OLLAMA_MODEL}")
    return ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=0.7,
        num_ctx=4096
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

