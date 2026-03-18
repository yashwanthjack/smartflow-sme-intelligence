# ⚡ SmartFlow OS

> **The AI-Native Financial Operating System for SMEs.**
> *Connected. Intelligent. Real-time.*

SmartFlow OS is a next-generation financial platform that acts as a **Fractional CFO** for businesses. It ingests messy financial data, normalizes it into a unified ledger, and uses AI Agents to provide strategic advice, cash flow forecasting, and risk intelligence.

---

## 🌟 Key Features

### 1. 📊 Real-Time Financial Dashboard
*   **Live Metrics**: Instant view of Cash Balance, Net Burn, Runway, and Net Income.
*   **Payments Waterfall**: Visual tracking of payment lifecycles (Initiated → Authorized → Settled).
*   **Gross Volume**: Revenue breakdown by channel (Online vs In-Store vs Subscriptions).

### 2. 🤖 AI Copilot & CFO Agents
*   **Natural Language Queries**: Ask *"What is my current runway?"* or *"Why is burn high this month?"*.
*   **Decision Advisor**: Creating "What-if" scenarios (e.g., *"Can I afford to hire a Senior Dev?"*) with real-time impact simulation.
*   **Credit Advisory**: Automated CFO-level health assessments and credit scoring.

### 3. 🛡️ Risk & Scenario Engine
*   **Risk Scorecard**: Live credit scoring based on cash flow patterns and counterparty risk.
*   **Scenario Simulator**: interactive tools to model expenses and revenue changes.
*   **Dark Forecast**: AI-driven predictions for future cash flow with confidence bands.

### 4. 🏢 Multi-Tenant & Secure
*   **Entity Isolation**: Full data separation for multiple organizations.
*   **Role-Based Access**: Granular permissions (Admin, Viewer, Lender).

---

## 🛠️ Tech Stack

### Frontend
*   **React 18**: Component-based UI architecture.
*   **Vite**: Blazing fast build tool.
*   **Recharts**: Interactive financial charting.
*   **Zentra Design System**: Custom glassmorphism UI with "Premium" aesthetics.

### Backend
*   **FastAPI**: High-performance Python web framework.
*   **PostgreSQL**: Robust relational database for financial ledgers.
*   **SQLAlchemy**: ORM for database interactions.

### AI & Intelligence
*   **LangChain**: Orchestration for AI Agents.
*   **Local LLM / Gemini**: Flexible support for multiple reasoning models.
*   **Pandas/NumPy**: Financial modeling and data transformation.

---

## 🚀 Getting Started

### Prerequisites
*   Node.js 18+
*   Python 3.10+
*   PostgreSQL

### 1. Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt

# Configure Database
# Set DATABASE_URL in .env (recommended) or edit backend/app/config.py.
# Example (PostgreSQL):
# DATABASE_URL=postgresql+psycopg2://postgres:<password>@<host>:5432/smartflow
# If your password contains '@', URL-encode it as '%40'.

# Run Server
uvicorn app.main:app --reload
```

### 2. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Seed Real Data (Optional)
To populate the dashboard with realistic financial history (Invoices, Transactions, Customers):
```bash
cd backend
python scripts/seed_data.py
```

---

## 📂 Project Structure

```
smartflow-sme-intelligence/
├── backend/
│   ├── app/
│   │   ├── agents/         # AI Logic (Decision Advisor, Credit Agent)
│   │   ├── models/         # Database Schema (Ledger, Entity, Account)
│   │   ├── routers/        # API Endpoints (Metrics, Data, Auth)
│   │   └── main.py         # App Entry Point
│   └── scripts/            # Utils (Seeding, Migration)
├── frontend/
│   ├── src/
│   │   ├── components/     # UI Blocks (MetricCard, Charts)
│   │   ├── pages/          # Full Views
│   │   └── App.jsx         # Main Layout
└── README.md
```

---

## 🔒 Security & Privacy
SmartFlow is designed with privacy first. 
*   **Data Isolation**: Every query is scoped to `entity_id`.
*   **No Training**: Customer data is *never* used to train public models.

---

**Built with ❤️ by YASH**
