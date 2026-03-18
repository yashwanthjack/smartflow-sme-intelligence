# FastAPI entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.db.database import engine, Base

# Import all models to register with SQLAlchemy (required before create_all)
from app.models.entity import Entity
from app.models.account import Account
from app.models.counterparty import Counterparty
from app.models.ledger_entry import LedgerEntry
from app.models.invoice import Invoice
from app.models.gst_summary import GSTSummary
from app.models.cash_flow import CashFlow
from app.models.credit_feature import CreditFeature
from app.models.audit_log import AuditLog
from app.models.case import Case
from app.models.user import User  # Auth model


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")
    
    # Start Agent Workforce background simulation
    # Temporarily disabled per user request
    # from app.services.agent_workforce import simulate_workforce
    # import asyncio
    # asyncio.create_task(simulate_workforce())
    
    yield
    # Shutdown: cleanup if needed
    print("Shutting down...")


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
  return {"status": "ok", "project": settings.PROJECT_NAME}

# Include Routers
from app.routers import ingest
from app.routers import agents
from app.routers import data
from app.routers import auth

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["Ingestion"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(data.router, prefix="/api/data", tags=["Data"])

# New Routers (Phase 1)
from app.routers import profile
from app.routers import organization

app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(organization.router, prefix="/api/org", tags=["Organization"])

# New Routers (Phase 2)
from app.routers import insights
app.include_router(insights.router, prefix="/api/insights", tags=["Insights"])
 

from app.routers import lender_api
app.include_router(lender_api.router, prefix="/api/lender", tags=["Lender Platform"])

# New Routers (Phase 6 - JACK Features)
from app.routers import simulation
app.include_router(simulation.router, prefix="/api/simulate", tags=["Simulation"])

# New Routers (Phase 8 - Real Data)
# New Routers (Phase 8 - Real Data)
from app.routers import metrics
app.include_router(metrics.router, prefix="/api")

# Phase 10 - Audit Trail
from app.routers import audit
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])
