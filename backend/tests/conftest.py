"""
Shared pytest fixtures for SmartFlow backend tests.
Provides test database, FastAPI TestClient, and mock LLM.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# Ensure backend is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Override DATABASE_URL to use in-memory SQLite for tests
os.environ["DATABASE_URL"] = "sqlite:///./test_smartflow.db"
os.environ["GOOGLE_API_KEY"] = "test-key-not-real"
os.environ["GEMINI_MODEL"] = "gemini-2.5-flash-lite"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient


# ── Database fixtures ─────────────────────────────────────────────────

@pytest.fixture(scope="session")
def test_engine():
    """Create a test SQLite engine (session-scoped for speed)."""
    db_path = "./test_smartflow.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    # On Windows, SQLite files may stay locked; clean up best-effort
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except PermissionError:
        pass  # File will be cleaned up on next run


@pytest.fixture
def db_session(test_engine):
    """Provide a transactional database session that rolls back after each test."""
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden DB dependency."""
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Mock LLM fixtures ────────────────────────────────────────────────

@pytest.fixture
def mock_llm():
    """A mocked LLM that returns a predictable response."""
    llm = MagicMock()
    llm.invoke.return_value = MagicMock(content="Mock LLM response for testing.")
    llm.ainvoke = AsyncMock(
        return_value=MagicMock(content="Mock async LLM response for testing.")
    )
    return llm


@pytest.fixture
def patch_llm(mock_llm):
    """Patch get_llm() globally so no real API calls are made during tests."""
    with patch("app.agents.llm.get_llm", return_value=mock_llm):
        yield mock_llm


# ── Sample data fixtures ─────────────────────────────────────────────

@pytest.fixture
def sample_entity_id():
    return "test-entity-001"


@pytest.fixture
def sample_ledger_entries(db_session, sample_entity_id):
    """Seed the test DB with sample ledger entries."""
    from app.models.ledger_entry import LedgerEntry
    from datetime import date, timedelta

    entries = []
    base_date = date.today() - timedelta(days=90)

    for i in range(90):
        entry_date = base_date + timedelta(days=i)
        # Alternate inflows and outflows
        amount = 50000 + (i * 100) if i % 3 != 0 else -(20000 + i * 50)
        entry = LedgerEntry(
            entity_id=sample_entity_id,
            ledger_date=entry_date,
            amount=amount,
            description=f"Test transaction day {i}",
            category="SALES" if amount > 0 else "EXPENSE",
            counterparty=f"Vendor_{i % 5}",
        )
        entries.append(entry)
        db_session.add(entry)

    db_session.commit()
    return entries
