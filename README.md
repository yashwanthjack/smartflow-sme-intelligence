# ⚡ SmartFlow SME Intelligence

> **The Multi-Agent Financial Operating System for Indian SMEs.**  
> *Autonomous. Intelligent. Real-time.*

SmartFlow is an AI-Native Financial OS that transforms messy bank statements, invoices, and GST data into a high-performance "Fractional CFO" workforce. Powered by **LangChain** and **Google Gemini 3.5 Flash Lite**, it doesn't just show you charts—it autonomously analyzes, reasons, and executes financial strategies.

---

## 🤖 The Autonomous Agentic Workforce

SmartFlow utilizes a **Hierarchical Multi-Agent Architecture** to process complex financial workflows:

-   **Executive Supervisor**: The brain of the system. It classifies user intent, recalls business-specific memories, and delegates tasks to specialized workers.
-   **Payments Agent**: Optimizes DPO (Days Payable Outstanding). It analyzes bank ledgers, identifies top spenders, and schedules optimized vendor payments to maintain cash safety.
-   **Collections Agent**: Reduces DSO (Days Sales Outstanding). It monitors overdue invoices and creates automated, context-aware collection plans.
-   **GST Compliance Agent**: Your tax expert. Reconciles GSTR-1/3B filings and ensures Input Tax Credit (ITC) is maximized and compliant.
-   **Credit Advisory Agent**: Calculates bank-standard Risk Scores and loan eligibility using cash-flow-based underwriting logic.
-   **Decision Advisor (CFO)**: Runs "What-If" simulations (e.g., Hiring, CAPEX) using real-time runway and burn rate data.

---

## ⚡ High-Performance Architecture & Automation

-   **High-Volume Parallel Processing**: Engineered to handle massive datasets securely. By implementing thread-safe SQLAlchemy Context Managers, SmartFlow's AI agents can query PostgreSQL in parallel without deadlocks.
-   **Automated Testing Pipeline**: Built with a comprehensive automated integration testing suite using `pytest` and `pytest-asyncio` to guarantee reliability, code quality, and seamless release testing.
-   **Real-time Intelligence**: Sub-second latency for dynamic calculations (e.g., exact 30-day net burn, runway forecasting) using a robust FastAPI REST backend.

---

## 🌟 Key Capabilities

### 1. 📊 Intelligent Financial Dashboard
*   **Live Metrics**: Bank Balance, Net Burn (180-day avg), and real-time Runway projections.
*   **Interactive Forecasting**: Powered by **Facebook Prophet**, projecting 30-60-90 day cash cycles with ML confidence bands.
*   **Activity Feed**: A real-time audit trail of every decision, tool-call, and interaction between agents.

### 2. 🧠 Persistent Agentic Memory
*   SmartFlow remembers your business rules (e.g., *"Wait 2 days before reminding Client X"*).
*   Agents recall past insights to ensure continuity in financial advice.

### 3. 🛡️ Enterprise-Grade Security
*   **Data Isolation**: Every agent interaction is strictly scoped to your unique `entity_id`.
*   **No Training**: Your financial secrets stay yours; data is never used for public model training.

---

## 🛠️ Technology Stack

-   **Frontend**: React 18, Vite, Recharts, Lucide Icons, Custom Glassmorphism CSS.
-   **Backend**: FastAPI, PostgreSQL, SQLAlchemy (with robust connection pooling).
-   **AI Orchestration**: LangGraph (Stateful Multi-Agent Graphs), LangChain.
-   **Intelligence Engine**: Google Gemini 3.5 Flash Lite, Facebook Prophet (ML Forecasting).
-   **Testing & CI/CD**: `pytest`, `pytest-asyncio`, FastAPI TestClient for automated integration environments.

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL instance running locally or on cloud

### 1. Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt

# Configure .env
# GOOGLE_API_KEY=your_gemini_api_key
# GEMINI_MODEL=gemini-2.5-flash-lite
# DATABASE_URL=postgresql://user:pass@localhost:5432/smartflow

uvicorn app.main:app --reload
```

### 2. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Run Tests
```bash
cd backend
pytest
```

### 4. Populate Data
Use the `App UI -> Upload Data` to ingest your bank statements or run the seeder:
```bash
python backend/populate_demo_data.py
```

---

**Built with ❤️ for the future of Indian SMEs by YASH**
