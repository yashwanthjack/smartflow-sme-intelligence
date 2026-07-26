# Playbook models for SmartFlow
# Reusable multi-step agent workflows that users can define and execute

from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, JSON, ForeignKey, func
from app.db.database import Base
import uuid


class Playbook(Base):
    __tablename__ = "playbooks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = Column(String, nullable=False, index=True)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # JSON array of step objects: [{order: 1, instruction: "...", agent_hint: "CollectionsAgent"}]
    steps = Column(JSON, nullable=False, default=[])

    # Optional cron expression for scheduled runs (future feature)
    schedule = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
    is_template = Column(Boolean, default=False)  # Built-in templates

    created_at = Column(DateTime, server_default=func.now())
    last_run_at = Column(DateTime, nullable=True)


class PlaybookRun(Base):
    __tablename__ = "playbook_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    playbook_id = Column(String, ForeignKey("playbooks.id"), nullable=False)
    entity_id = Column(String, nullable=False, index=True)

    # Status: running | completed | failed
    status = Column(String, nullable=False, default="running")

    # JSON array of per-step outputs: [{step: 1, instruction: "...", output: "...", success: true}]
    step_results = Column(JSON, nullable=False, default=[])

    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
