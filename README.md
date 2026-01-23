# SmartFlow — Multi-Agent AI for Cash-Flow Forecasting & Credit Intelligence (Indian SMEs)

SmartFlow is an **AI governance + intelligence layer for Indian SME credit underwriting**.  
It ingests **bank statements**, **Tally/Zoho exports**, and **GST filings** to generate:

✅ **30/60/90-day cash-flow forecasts + cash runway**  
✅ **Lightweight credit score + PD band**  
✅ **Declarative credit policies (BLOCK/WARN/SAFE)**  
✅ **Working-capital optimization suggestions**  
✅ **LLM-generated credit memo + reviewer checks**  
✅ **Audit trail + decision replay**

> SmartFlow is **not a lender**. It is a credit intelligence backend that helps lenders/fintechs make faster and more consistent SME credit decisions.

---

## Table of Contents

- [Why SmartFlow](#why-smartflow)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Agent Pipeline](#agent-pipeline)
- [Tech Stack](#tech-stack)
- [API (MVP)](#api-mvp)
- [Quickstart](#quickstart)
- [Configuration](#configuration)
- [Roadmap](#roadmap)
- [References / Inspiration Papers](#references--inspiration-papers)
- [License](#license)

---

## Why SmartFlow

Indian SME underwriting is often messy because data is fragmented:

- Bank statement ≠ ledger revenue ≠ GST turnover
- Cash flow is volatile and seasonal
- Policy checks are manual and inconsistent

SmartFlow solves this by acting as a **governed, auditable multi-agent AI pipeline** that produces:

- reliable cash-flow intelligence
- risk signals
- transparent policy evaluation
- a lender-ready credit memo

---

## Key Features

### 1) Data ingestion

Upload:

- SME **bank statements** (CSV)
- **Ledger exports** (Tally/Zoho CSV/XLSX)
- **GST summary files** (JSON/PDF → extracted)

Output normalized tables:

- `cash_flows_daily`
- `features_credit`
- `gst_summary`

---

### 2) Cash-flow forecasting

- Aggregates inflows/outflows daily/weekly
- Uses **Prophet** to forecast:
  - 30 / 60 / 90-day cash flows
  - cash runway estimates

---

### 3) Credit scoring & PD banding

Computes underwriting features:

- Avg monthly inflow + volatility
- Negative cash months / overdrafts
- Customer concentration (top-N)
- GST consistency (filing delays, gaps)

Outputs:

- Score (0–100)
- PD band: `LOW | MEDIUM | HIGH`
- Red flags:
  - sharp drops in revenue
  - high concentration
  - missed GST periods

---

### 4) Policy engine & risk guards (declarative)

Policies are defined in JSON/YAML, e.g.:
max_loan_multiple_of_inflow: 3
min_runway_days_after_emi: 30
reject_if_consecutive_gst_missed: 2

```yaml



                    +----------------------+
                    |  Frontend (React)    |
                    | upload + dashboard   |
                    +----------+-----------+
                               |
                               v
+------------------+     +---------------------+
|  Bank CSV / GST  | --> |   FastAPI Backend   |
|  Ledger Exports  |     | ingest + case mgmt  |
+------------------+     +----------+----------+
                                   |
                                   v
                +----------------------------------+
                | Multi-Agent Pipeline (SmartFlow) |
                +----------------------------------+
                | Data Agent        -> normalized  |
                | Risk Agent        -> score/PD    |
                | Policy Agent      -> SAFE/WARN   |
                | Optimization Agent-> actions     |
                | Narrative Agent   -> memo        |
                | Reviewer Agent    -> critique    |
                +------------------+---------------+
                                   |
                                   v
                         +------------------+
                         | Postgres/SQLite  |
                         | logs + audit     |
                         +------------------+

```

## Agent Pipeline

### 🧩 Agents

- **Data Agent**
  - Cleans & joins bank, ledger, and GST data
  - Outputs normalized datasets

- **Risk Agent**
  - Uses forecast results + credit features
  - Produces risk metrics, credit score, and PD band

- **Policy Agent**
  - Executes declarative underwriting rules
  - Aggregates recommendations into `SAFE / WARN / BLOCK`

- **Optimization Agent**
  - Suggests invoice collections & payable delays
  - Estimates liquidity impact

- **Narrative Agent**
  - Generates lender-style memo using structured facts

- **Reviewer Agent**
  - Validates memo vs facts (numbers, flags)
  - Reports contradictions / missing logic

---

## Tech Stack

### Backend
- Python 3.10+
- FastAPI + Uvicorn/Gunicorn
- Pandas / NumPy
- Prophet (forecasting)
- XGBoost (scoring)
- SQLAlchemy
- PostgreSQL (prod) / SQLite (dev)
- Optional: FAISS + SentenceTransformers (RAG)
- Optional: MLflow, Prometheus client

### Frontend
- React / Next.js
- Charts: Recharts / Chart.js
- Case dashboard: SAFE/WARN/BLOCK flags
- Memo editing + export to PDF

### Infra
- Docker + Docker Compose
- Poetry or pip/venv



## API (MVP)

> Base URL: `http://localhost:8000`

| Endpoint | Method | Description |
|---------|--------|-------------|
| `/ingest` | POST | Upload bank, ledger, GST files → returns `case_id` |
| `/case/{case_id}/summary` | GET | Structured summary (features, scores, flags) |
| `/case/{case_id}/forecast` | GET | Cash-flow forecast outputs |
| `/case/{case_id}/memo` | GET | Generated credit memo |
| `/case/{case_id}/policy` | GET | Policy evaluation results |
| `/case/{case_id}/audit` | GET | Decision logs + overrides |

### Upload Example

`POST /ingest`

```json
{
  "case_id": "uuid-1234",
  "status": "ingested"
}

```

## Roadmap

- [ ] Better SME cash-flow decomposition (seasonality, vendor cycles)
- [ ] Stronger PD model benchmarking (Indian SME datasets)
- [ ] Explainable model outputs (feature attribution)
- [ ] Full RAG support over PDFs (GST returns / bank notes)
- [ ] Multi-tenant SaaS mode (per-lender policies)
- [ ] Automated bias checks + HITL review console
- [ ] Production observability (traces + drift monitoring)

---

## References / Inspiration Papers

SmartFlow’s architecture draws concepts from recent agentic finance research:

1) **FINCON — Synthesized LLM Multi-Agent System with Conceptual Verbal Reinforcement**
   - manager–analyst hierarchy  
   - risk-control / tail-risk adaptation  

2) **MASFIN — Multi-Agent System for Decomposed Financial Reasoning and Forecasting**
   - staged pipelines + HITL  
   - bias-aware evaluation  

3) **JPMorgan EMNLP Industry Track — Multi-Agent Framework for Quantitative Finance**
   - specialized agent roles  
   - code-executing + reflection agents  

> These works are conceptual references; SmartFlow implements a practical SME underwriting subset.
