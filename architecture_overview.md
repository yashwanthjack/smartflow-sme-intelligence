# SmartFlow OS Architecture

This document illustrates the technical architecture of SmartFlow OS, highlighting the integration of the React frontend, FastAPI backend, specialized AI Agents, and the underlying data infrastructure.

## System Diagram

```mermaid
graph TD
    classDef frontend fill:#1e293b,stroke:#6366f1,stroke-width:2px,color:#fff;
    classDef backend fill:#0f172a,stroke:#10b981,stroke-width:2px,color:#fff;
    classDef service fill:#312e81,stroke:#a855f7,stroke-width:2px,color:#fff;
    classDef infra fill:#374151,stroke:#f59e0b,stroke-width:2px,color:#fff;
    classDef external fill:#4b5563,stroke:#9ca3af,stroke-width:2px,border-style:dashed,color:#fff;

    subgraph Frontend [Running on Client Browser]
        direction TB
        App[React 18 + Vite App]:::frontend
        App --> Dashboard[SaaS Dashboard]:::frontend
        App --> DPI[DPI Stack Hub]:::frontend
        App --> GST[GST Recon Engine]:::frontend
        App --> Credit[OCEN Credit Marketplace]:::frontend
        App --> Chain[Supply Chain Score]:::frontend
        App --> Copilot[Copilot Interface]:::frontend
    end

    subgraph Backend [FastAPI Server]
        direction TB
        API[API Gateway / Routers]:::backend
        Auth[Auth Service]:::backend
        Orch[LangChain Orchestrator]:::backend
        
        API --> Auth
        API --> Orch
        
        subgraph AgentLayer [Multi-Agent System]
            Sup[Supervisor Agent]:::service
            Judge[Judge Agent (Guardrail)]:::service
            Adv[Decision Advisor]:::service
            Col[Collections Agent]:::service
            Risk[Credit Advisory Agent]:::service
            Tax[GST Compliance Agent]:::service
            
            Orch --> Sup
            Sup --> Judge
            Sup --> Adv
            Sup --> Col
            Sup --> Risk
            Sup --> Tax
        end

        subgraph CoreServices [Predictive Services]
            Score[Scoring Service (XGBoost)]:::service
            Forecast[Forecasting Service (LSTM+Prophet)]:::service
            Health[Health Pulse Engine]:::service
            Ingest[Ingestion Pipeline]:::service
            
            Risk --> Score
            Adv --> Forecast
            API --> Health
            API --> Ingest
        end
    end

    subgraph Infrastructure [Data & Compute]
        DB[(PostgreSQL / SQLite)]:::infra
        Vector[(ChromaDB Vector Store)]:::infra
        LLM[Gemini Pro LLM API]:::infra
    end

    subgraph Ecosystem [External Systems]
        AA[Account Aggregator]:::external
        OCEN[OCEN Protocol]:::external
        GSTN[GSTN API]:::external
    end

    %% Connections
    Frontend -- REST API --> API
    API -- Reads/Writes --> DB
    Ingest -- Embeddings --> Vector
    Orch -- Context --> Vector
    Orch -- Prompts --> LLM
    Score -- Reads --> DB
    Forecast -- Reads --> DB
    
    %% External Integrations
    Ingest <-- Data Sync --> AA
    Tax <-- Recon --> GSTN
    Credit <-- Application --> OCEN
    
    %% HITL Feedback
    Judge -.->|Safety Feedback| User((User))
```

## Key Components

### 1. Frontend Layer (React + Vite)
- **SaaS Dashboard**: Real-time financial monitoring.
- **DPI Stack Hub**: Central interface for India Stack integrations (AA, OCEN).
- **GST Reconciliation**: Automated purchase register matching.
- **Credit Marketplace**: Flow-based credit offers.
- **Copilot**: Natural language interface to financial agents.

### 2. Backend Layer (FastAPI)
- **Agent Orchestrator**: Manages the lifecycle and tool execution of AI agents using LangChain.
- **Specialized Agents**:
  - **Supervisor**: Routes user intents.
  - **Judge**: Validates high-stakes financial advice.
  - **Decision Advisor**: Runs "What-If" simulations.
  - **Collections/GST/Credit**: Domain-specific execution agents.

### 3. Predictive Services
- **Scoring Service**: Hybrid XGBoost + Heuristic model for accurate credit assessment.
- **Forecasting Service**: Prophet + Moving Average ensemble for cash flow prediction.
- **Health Pulse**: Real-time business health metric aggregation.

### 4. Infrastructure
- **Databases**: Relational storage for transactions; Vector store for RAG.
- **LLM**: Powered by Google Gemini Pro for reasoning and extraction.
