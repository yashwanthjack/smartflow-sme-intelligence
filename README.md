# SmartFlow — SME Intelligence (CFO Brain API)

**SmartFlow** is an agentic AI backend that gives any product a **“CFO brain” for Small & Medium Businesses (SMEs)**.  
It exposes a set of REST APIs that provide:

- **Cash-flow forecasting**
- **Credit intelligence**
- **Working-capital optimization**
- **Basic compliance checks**

> ✅ SmartFlow is **not a lender**.  
> It is *lending decision support infrastructure* — it analyzes SME financial data and returns cash-flow + credit risk intelligence that banks, fintechs, neobanks, or DeFi protocols can plug into their workflows.

---

## ✨ Features

### ✅ REST APIs
- **`POST /forecast`** – Predict **30/60/90-day cash flow** from transaction history.
- **`POST /credit-score`** – Score SME creditworthiness with **PD estimate + explanation**.
- **`POST /optimize`** – Recommend invoices to collect + payables to delay to improve working capital.
- **`POST /compliance-check`** – Simple compliance risk checks (GST/tax signals).

### 🤖 RAG-backed Agents
SmartFlow uses retrieval-augmented agents that can read and reason over:
- Tally exports
- Bank transaction CSVs
- GST / compliance PDFs

Vector database used: **FAISS**.

### 🛡️ Hallucination-safe System
LLM outputs are validated against retrieved documents.
When uncertain, SmartFlow falls back to **classical ML models**:
- **Prophet** for time series forecasting
- **XGBoost** for credit scoring

Includes a **hallucination detector** using similarity scoring between:
- retrieved documents  
- generated response  

### 📊 MLOps-ready
Includes production-friendly tooling:
- **MLflow** (tracking, metrics, model registry)
- **Prometheus metrics**
  - latency
  - error rate
  - hallucination rate

---

## 🧱 Architecture Overview

```txt
Client (fintech / tool / neobank / DeFi)
        │
        ▼
FastAPI REST API
  - POST /forecast
  - POST /credit-score
  - POST /optimize
  - POST /compliance-check
        │
        ▼
Agent Orchestrator (ReAct-style)
  - Forecast Agent
  - Credit Agent
  - Optimize Agent
  - Compliance Agent
        │
        ▼
AI & ML Layer
  - LLM (Mistral / LLaMA) + LoRA adapter
  - RAG: sentence-transformers embeddings + FAISS vector DB
  - Classical ML fallback: Prophet (forecast), XGBoost (credit)
  - Hallucination detector (similarity vs retrieved docs)
        │
        ▼
Data & MLOps Layer
  - PostgreSQL / SQLite (SME data, logs, audit trail)
  - FAISS Index (vector search over documents)
  - MLflow (model registry + tracking)
  - Prometheus metrics (latency, error, hallucination)
```


🧰 Tech Stack
Backend

FastAPI

Uvicorn

Pydantic

LLM / Agents

Mistral / LLaMA family (Hugging Face or API)

LoRA adapters (PEFT)

ReAct-style agent orchestration

RAG

sentence-transformers/all-MiniLM-L6-v2

FAISS vector database

Classical ML

Prophet (cash-flow forecast)

XGBoost (credit scoring)

Data

PostgreSQL (prod)

SQLite (dev)

MLOps + Monitoring

MLflow

Prometheus client

Infra

Docker

Docker Compose

🚀 Getting Started
1) Clone Repo
git clone https://github.com/yashwanthjack/smartflow-sme-intelligence.git
cd smartflow-sme-intelligence

2) Create Virtual Env
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

3) Install Dependencies
pip install -r requirements.txt

4) Run API Server
uvicorn app.main:app --reload


API will be available at:

http://127.0.0.1:8000

Swagger docs: http://127.0.0.1:8000/docs

### 📌 API Endpoints
✅ Forecast

POST /forecast
Predict cash flow for 30/60/90 days using transaction history.

✅ Credit Score

POST /credit-score
Returns:

credit risk score

PD probability

explanation (RAG evidence-backed)

✅ Optimize Working Capital

POST /optimize
Returns recommendations to:

collect invoices faster

delay payables smartly

optimize cash cycle

✅ Compliance Check

POST /compliance-check
Runs simple checks for:

GST/tax risk flags

missing payments

compliance anomalies

🧠 How It Works

User uploads SME data (bank CSV / Tally exports / GST PDFs)

Documents are chunked + embedded (sentence-transformers)

Stored in FAISS for semantic retrieval

Agent selects tools + retrieves relevant evidence

LLM produces response using retrieved evidence

Hallucination detection validates output

If uncertain → fallback ML model response is returned

🤝 Contributing

Contributions are welcome — this project is a strong playground for:

LLMs + RAG

Agentic AI

MLOps / production ML

Financial data modeling

Ideas for Contributions

New optimization strategies and rules

Better feature engineering for credit scoring

Support additional vector DBs (Qdrant, Pinecone, etc.)

Dashboards and monitoring improvements

Tutorials and example client apps

📫 Contact

Maintainer: Yashwanth R
📩 Email: yashwanthrajeshkumar@gmail.com

🐙 GitHub: @yashwanthjack

If you are using SmartFlow in a project (fintech app, hackathon, research), feel free to open an issue or PR — would love to see how you’re extending it 🚀
