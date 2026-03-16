graph TD
    %% Styling
    classDef frontend fill:#1e1e1e,stroke:#4a90e2,stroke-width:2px,color:#fff
    classDef backend fill:#1e1e1e,stroke:#e24a4a,stroke-width:2px,color:#fff
    classDef algo fill:#1e1e1e,stroke:#f5a623,stroke-width:2px,color:#fff
    classDef data fill:#1e1e1e,stroke:#50e3c2,stroke-width:2px,color:#fff
    classDef component fill:#333,stroke:#666,stroke-width:1px,color:#fff

    subgraph Frontend [Frontend (React + Vite)]
        direction TB
        LenderDash[Lender Dashboard]:::component
        SMEDash[SME Dashboard]:::component
        AuthPage[Login / Auth]:::component
    end

    subgraph Backend [Backend (FastAPI + Python)]
        direction TB
        API[REST API Layer]:::component
        
        subgraph Services [Core Services]
            direction TB
            IngestSvc[Ingestion Service]:::component
            ForecastSvc[Forecasting Service]:::component
            AgentSvc[Agent Workforce]:::component
            ScoringSvc[Scoring Service]:::component
        end

        subgraph Agents [AI Agent System]
            direction TB
            Supervisor[Supervisor Agent]:::component
            CreditAgent[Credit Advisory]:::component
            CollectAgent[Collections Agent]:::component
            DecisionAgent[Decision Advisor]:::component
        end
    end

    subgraph AI_Layer [AI / Algo Layer]
        direction TB
        Prophet[Prophet / ARIMA]:::component
        ML_Models[XGBoost / Sklearn]:::component
        LLM_Engine[LangChain / LLM]:::component
    end

    subgraph Data_Layer [Data Layer]
        direction TB
        DB[(PostgreSQL / SQLite)]:::component
        Redis[(Redis Cache)]:::component
    end

    %% Connections
    LenderDash --> API
    SMEDash --> API
    AuthPage --> API

    API --> IngestSvc
    API --> ForecastSvc
    API --> AgentSvc
    API --> ScoringSvc

    AgentSvc --> Supervisor
    Supervisor --> CreditAgent
    Supervisor --> CollectAgent
    Supervisor --> DecisionAgent

    ForecastSvc --> Prophet
    ScoringSvc --> ML_Models
    Supervisor --> LLM_Engine

    IngestSvc --> DB
    ForecastSvc --> DB
    ScoringSvc --> DB
    AgentSvc --> DB

    %% Styles
    class Frontend frontend
    class Backend backend
    class AI_Layer algo
    class Data_Layer data