# SmartFlow — Multi-Agent AI for Cash Flow Forecasting & Credit Intelligence

> **A CFO's brain for Indian SMEs** — combining cash forecasting, credit scoring, and agentic workflows into one intelligent platform.

SmartFlow is an AI-native financial operating system that ingests bank statements, Tally/ERP exports, and GST filings to deliver:

✅ **7/30/90-day cash-flow forecasts** with runway alerts  
✅ **Credit scoring & risk intelligence** (counterparty + SME-level)  
✅ **Agentic workflows** — Collections, Payments, GST, Credit Advisory  
✅ **Unified financial ledger** from fragmented data sources  
✅ **APIs for lenders/fintechs** to embed credit intelligence  

---

## The Problem

Indian MSMEs face a **₹530B credit gap** — only ~14% of 63M+ businesses get formal credit.

| Pain Point | Reality |
|------------|---------|
| No predictive intelligence | SMEs manage cash in spreadsheets with zero visibility |
| Opaque credit decisions | Banks use slow, document-heavy, collateral-based models |
| Fragmented tools | Payments, accounting, compliance exist separately |

---

## The Solution

SmartFlow acts as a **governed, auditable multi-agent AI pipeline** that:

1. **Ingests** messy financial data (Bank CSV, Tally exports, GST returns)
2. **Normalizes** into a unified time-indexed ledger
3. **Predicts** cash flows using Prophet-style models
4. **Scores** credit risk using XGBoost on GST + bank behavior
5. **Acts** via specialized agents that do real work

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Experience Layer                         │
│            Dashboard  •  APIs  •  Alerts                    │
├─────────────────────────────────────────────────────────────┤
│                     Agentic Layer                           │
│  CollectionsAgent • PaymentsAgent • GSTAgent • CreditAgent  │
├─────────────────────────────────────────────────────────────┤
│                   Intelligence Layer                        │
│         Prophet Forecasting  •  XGBoost Risk Scoring        │
├─────────────────────────────────────────────────────────────┤
│                   Canonical Data Model                      │
│   Entity • Counterparty • Account • Invoice • LedgerEntry   │
├─────────────────────────────────────────────────────────────┤
│                    Ingestion Layer                          │
│          Bank Parser  •  Tally Parser  •  GST Parser        │
└─────────────────────────────────────────────────────────────┘
```

---

## Agents

| Agent | What It Does |
|-------|--------------|
| **Collections Agent** | Ranks customers by risk, drafts payment reminders |
| **Payments Agent** | Schedules payments to minimize cash gaps |
| **GST Agent** | Monitors filings, flags blocked credits |
| **Credit Advisory Agent** | Recommends internal vs external funding |

Each agent outputs **actions + reasoning** — transparent, auditable, overridable.

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.10+, FastAPI, SQLAlchemy, PostgreSQL |
| **Modeling** | Prophet (forecasting), XGBoost (credit/risk) |
| **Agents** | LangGraph / Custom orchestrator |
| **Frontend** | React, Recharts |
| **Infra** | Docker, Docker Compose |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ingest` | POST | Upload bank/ledger/GST files |
| `/api/entities/{id}/forecast` | GET | Cash-flow forecast |
| `/api/entities/{id}/risk-score` | GET | Credit score + PD band |
| `/api/entities/{id}/collections-plan` | GET | Prioritized collection actions |
| `/api/entities/{id}/payments-schedule` | GET | Optimized payment calendar |

---

## Quickstart

```bash
# Clone the repo
git clone https://github.com/your-org/smartflow-sme-intelligence.git
cd smartflow-sme-intelligence

# Setup backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Visit http://localhost:8000/docs
```

---

## Roadmap

- [ ] Bank account API integrations (AA framework)
- [ ] GST portal direct sync
- [ ] WhatsApp bot for collections
- [ ] Lender API marketplace
- [ ] Production observability (traces + drift monitoring)

---

## License

MIT

---

> **SmartFlow is not a lender.** It's the intelligence layer that helps lenders and fintechs make faster, more consistent SME credit decisions.
