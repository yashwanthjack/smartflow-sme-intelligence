import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
MODEL = os.getenv("HF_MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")

print(f"Testing HF API with Model: {MODEL}")
print(f"Token present: {bool(TOKEN)}")

try:
    client = InferenceClient(token=TOKEN)
    # Chat completion test
    response = client.chat_completion(
        messages=[{"role": "user", "content": "Hello, are you working?"}],
        model=MODEL, 
        max_tokens=50
    )
    print(f"✅ Success! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Failed: {e}")
