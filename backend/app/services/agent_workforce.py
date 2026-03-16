import random
import asyncio
import traceback
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.audit_log import AuditLog
from app.models.entity import Entity
from app.agents.llm import get_llm


class AgentWorkforceService:
    def __init__(self, db: Session):
        self.db = db
        try:
            self.llm = get_llm()
        except Exception:
            self.llm = None

    async def _generate_text(self, prompt: str, fallback: str) -> str:
        """Helper to generate text with LLM or return fallback."""
        if not self.llm:
            return fallback
        try:
            # ainvoke is asynchronous and won't block the event loop
            response = await self.llm.ainvoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"LLM gen failed: {e}")
            return fallback

    def _get_random_customer(self, entity_id):
        """Get a random customer from ledger (inflow transactions)."""
        from app.models.ledger_entry import LedgerEntry
        try:
            # simple heuristic: positive amount = customer paying us
            customers = self.db.query(LedgerEntry.description)\
                .filter(LedgerEntry.entity_id == entity_id, LedgerEntry.amount > 0)\
                .distinct().limit(50).all()
            
            if customers:
                return random.choice(customers)[0]
        except Exception:
            pass
        return None

    def _get_random_vendor(self, entity_id):
        """Get a random vendor from ledger (outflow transactions)."""
        from app.models.ledger_entry import LedgerEntry
        try:
            # simple heuristic: negative amount = us paying vendor
            vendors = self.db.query(LedgerEntry.description)\
                .filter(LedgerEntry.entity_id == entity_id, LedgerEntry.amount < 0)\
                .distinct().limit(50).all()
            
            if vendors:
                return random.choice(vendors)[0]
        except Exception:
            pass
        return None

    async def run_background_cycle(self, entity_id: str):
        """Simulates multi-agent orchestration for an entity."""
        
        # Each cycle: run 1 multi-agent scenario + 1-2 individual agent tasks
        scenario = random.choice([
            self._scenario_collections_credit,
            self._scenario_cashflow_payments,
            self._scenario_gst_risk,
            self._scenario_forecast_collections,
            self._scenario_risk_payments_cashflow,
            self._scenario_full_sweep,
        ])
        
        await scenario(entity_id)

    # ======================================================================
    # MULTI-AGENT INTERACTION SCENARIOS
    # ======================================================================

    async def _scenario_collections_credit(self, entity_id: str):
        """CollectionsBot detects overdue → asks RiskSentinel for risk score → decides action."""
        customer = self._get_random_customer(entity_id)
        if not customer: return  # Skip simulation if no real data
        
        trace_id = f"trace-{uuid.uuid4().hex[:8]}"
        
        overdue_amount = random.randint(50000, 300000)
        days_overdue = random.randint(5, 60)
        risk_score = random.randint(350, 800)
        risk_band = "A" if risk_score > 700 else ("B" if risk_score > 550 else "C")
        
        # Step 1: CollectionsBot finds overdue
        prompt_detect = f"""You are a Collections Agent. A customer '{customer}' has an overdue invoice of ₹{overdue_amount:,} ({days_overdue} days late).
        Write a concise 1-sentence audit log summary about detecting this. Tone: Professional but alert."""
        
        summary_detect = await self._generate_text(prompt_detect, f"Found overdue invoice from {customer}: ₹{overdue_amount:,} ({days_overdue} days overdue)")
        
        await self._log(entity_id, trace_id, "CollectionsBot", "OVERDUE_DETECTED",
            severity="WARNING",
            summary=summary_detect,
            details={"customer": customer, "amount": overdue_amount, "days_overdue": days_overdue,
                     "next_action": "Requesting risk assessment from RiskSentinel"})
        
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        # Step 2: CollectionsBot → RiskSentinel (cross-agent request)
        prompt_req = f"""You are RiskSentinel. CollectionsBot asked you to assess '{customer}'.
        Write a concise 1-sentence audit log summary acknowledging the request."""
        
        summary_req = await self._generate_text(prompt_req, f"📨 Received request from CollectionsBot → Assessing {customer} risk profile")

        await self._log(entity_id, trace_id, "RiskSentinel", "RISK_SCORE_REQUESTED",
            severity="INFO",
            summary=summary_req,
            details={"requested_by": "CollectionsBot", "target": customer, "risk_score": risk_score,
                     "risk_band": risk_band, "payment_history": f"{random.randint(1,5)} late payments in 6 months"})
        
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        # Step 3: RiskSentinel responds → CollectionsBot decides
        if risk_band == "C":
            risk_desc = "High Risk"
            sev = "CRITICAL"
        elif risk_band == "B":
            risk_desc = "Medium Risk"
            sev = "WARNING"
        else:
            risk_desc = "Low Risk"
            sev = "INFO"

        prompt_action = f"""You are CollectionsBot. RiskSentinel reported '{customer}' is {risk_desc} (Score {risk_score}).
        Decide on an action (Urgent notice / Firm reminder / Gentle nudge).
        Write a concise 1-sentence audit log summary of your decision."""
        
        summary_action = await self._generate_text(prompt_action, f"📋 Decision based on RiskSentinel analysis → {risk_desc} action taken.")

        await self._log(entity_id, trace_id, "CollectionsBot", "DECISION_MADE",
            severity=sev,
            summary=summary_action,
            details={"decided_by": "CollectionsBot", "informed_by": "RiskSentinel",
                     "risk_score": risk_score, "risk_band": risk_band,
                     "confidence": round(random.uniform(0.88, 0.99), 2)})

    async def _scenario_cashflow_payments(self, entity_id: str):
        """CashFlowGuard detects low runway → tells PaymentsOptimizer to delay non-critical payments."""
        trace_id = f"trace-{uuid.uuid4().hex[:8]}"
        
        runway_days = random.randint(8, 45)
        burn_rate = random.randint(80000, 200000)
        
        # Step 1: CashFlowGuard analyzes
        sev = "CRITICAL" if runway_days < 15 else ("WARNING" if runway_days < 30 else "INFO")
        await self._log(entity_id, trace_id, "CashFlowGuard", "RUNWAY_ANALYSIS",
            severity=sev,
            summary=f"Cash runway: {runway_days} days at ₹{burn_rate:,}/day burn rate. {'⚠️ Alerting PaymentsOptimizer!' if runway_days < 30 else '✅ Healthy runway.'}",
            details={"runway_days": runway_days, "burn_rate": burn_rate,
                     "alert_sent_to": "PaymentsOptimizer" if runway_days < 30 else None})
        
        if runway_days < 30:
            await asyncio.sleep(random.uniform(0.3, 0.8))
            
            savings = random.randint(15000, 75000)
            delayed_count = random.randint(2, 5)
            
            # Step 2: PaymentsOptimizer receives alert and acts
            await self._log(entity_id, trace_id, "PaymentsOptimizer", "PAYMENT_RESCHEDULED",
                severity="WARNING",
                summary=f"📨 Received alert from CashFlowGuard (runway={runway_days}d) → Delaying {delayed_count} non-critical payments, saving ₹{savings:,}",
                details={"triggered_by": "CashFlowGuard", "payments_delayed": delayed_count,
                         "estimated_savings": savings, "new_runway": runway_days + random.randint(5, 12),
                         "critical_payments_preserved": True})
            
            await asyncio.sleep(random.uniform(0.2, 0.5))
            
            # Step 3: CashFlowGuard acknowledges new runway
            new_runway = runway_days + random.randint(5, 12)
            await self._log(entity_id, trace_id, "CashFlowGuard", "RUNWAY_UPDATED",
                severity="INFO",
                summary=f"✅ PaymentsOptimizer extended runway to {new_runway} days. Cash position stabilized.",
                details={"old_runway": runway_days, "new_runway": new_runway,
                         "collaboration": "CashFlowGuard ↔ PaymentsOptimizer"})

    async def _scenario_gst_risk(self, entity_id: str):
        """GSTComplianceAgent finds mismatch → RiskSentinel updates credit risk."""
        vendor = self._get_random_vendor(entity_id)
        if not vendor: return
        
        trace_id = f"trace-{uuid.uuid4().hex[:8]}"
        
        mismatches = random.randint(1, 6)
        itc_blocked = random.randint(10000, 80000)
        
        # Step 1: GST finds issues
        prompt_gst = f"""You are GSTComplianceAgent. You found {mismatches} mismatches in GSTR-2A for vendor '{vendor}'.
        Total ITC blocked: ₹{itc_blocked:,}.
        Write a concise 1-sentence audit log summary reporting this issue to RiskSentinel."""
        
        summary_gst = await self._generate_text(prompt_gst, f"GSTR-2A reconciliation found {mismatches} mismatches. ₹{itc_blocked:,} ITC blocked due to {vendor} non-filing.")
        
        await self._log(entity_id, trace_id, "GSTComplianceAgent", "RECONCILIATION_ALERT",
            severity="WARNING",
            summary=summary_gst,
            details={"mismatches": mismatches, "itc_blocked": itc_blocked,
                     "non_compliant_vendor": vendor, "alerting": "RiskSentinel"})
        
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        # Step 2: RiskSentinel reacts
        score_impact = random.randint(-45, -15)
        prompt_risk = f"""You are RiskSentinel. GSTComplianceAgent reported {vendor} is non-compliant (ITC blocked ₹{itc_blocked:,}).
        You are lowering credit score by {score_impact} points.
        Write a concise 1-sentence audit log summary of your action."""
        
        summary_risk = await self._generate_text(prompt_risk, f"📨 Received GST alert → Adjusting credit score by {score_impact} points. Vendor {vendor} flagged for review.")

        await self._log(entity_id, trace_id, "RiskSentinel", "SCORE_ADJUSTMENT",
            severity="WARNING",
            summary=summary_risk,
            details={"triggered_by": "GSTComplianceAgent", "score_impact": score_impact,
                     "vendor_flagged": vendor, "recommendation": "Withhold payment until vendor files returns"})
        
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        # Step 3: GST agent acknowledges
        prompt_ack = f"""You are GSTComplianceAgent. RiskSentinel confirmed action on {vendor}.
        You are sending a compliance reminder.
        Write a concise 1-sentence audit log summary."""
        
        summary_ack = await self._generate_text(prompt_ack, f"✅ RiskSentinel confirmed. Auto-drafting compliance reminder to {vendor}. ITC recovery plan initiated.")

        await self._log(entity_id, trace_id, "GSTComplianceAgent", "VENDOR_ACTION",
            severity="INFO",
            summary=summary_ack,
            details={"vendor": vendor, "action": "compliance_reminder_sent",
                     "collaboration": "GSTComplianceAgent ↔ RiskSentinel"})

    async def _scenario_forecast_collections(self, entity_id: str):
        """ForecastEngine predicts revenue dip → CollectionsBot accelerates collection."""
        trace_id = f"trace-{uuid.uuid4().hex[:8]}"
        
        dip_pct = random.randint(10, 35)
        dip_month = random.choice(["March", "April", "May"])
        
        # Step 1: Forecast detects dip
        await self._log(entity_id, trace_id, "ForecastEngine", "REVENUE_FORECAST_ALERT",
            severity="WARNING",
            summary=f"Prophet model predicts {dip_pct}% revenue dip in {dip_month}. Alerting CollectionsBot to accelerate receivables.",
            details={"dip_pct": dip_pct, "month": dip_month, "model": "Prophet",
                     "confidence": round(random.uniform(0.82, 0.95), 2), "alerting": "CollectionsBot"})
        
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        # Step 2: CollectionsBot responds
        invoices_targeted = random.randint(3, 8)
        amount_targeted = random.randint(100000, 500000)
        await self._log(entity_id, trace_id, "CollectionsBot", "ACCELERATED_COLLECTION",
            severity="WARNING",
            summary=f"📨 Received forecast alert → Targeting {invoices_targeted} invoices (₹{amount_targeted:,}) for accelerated collection before {dip_month}.",
            details={"triggered_by": "ForecastEngine", "invoices_targeted": invoices_targeted,
                     "amount": amount_targeted, "deadline": f"Before {dip_month} 1st",
                     "strategy": "Priority calls + early payment discounts offered"})

    async def _scenario_risk_payments_cashflow(self, entity_id: str):
        """Three-agent chain: RiskSentinel flags → PaymentsOptimizer adjusts → CashFlowGuard validates."""
        supplier = self._get_random_vendor(entity_id)
        if not supplier: return
        
        trace_id = f"trace-{uuid.uuid4().hex[:8]}"
        
        risk_level = random.choice(["HIGH", "CRITICAL"])
        amount_at_risk = random.randint(50000, 200000)
        
        # Step 1: RiskSentinel flags supplier
        await self._log(entity_id, trace_id, "RiskSentinel", "SUPPLIER_RISK_ALERT",
            severity="CRITICAL" if risk_level == "CRITICAL" else "WARNING",
            summary=f"🚨 Supplier {supplier} flagged as {risk_level} risk. ₹{amount_at_risk:,} exposure. Alerting PaymentsOptimizer.",
            details={"supplier": supplier, "risk_level": risk_level, "exposure": amount_at_risk,
                     "alerting": ["PaymentsOptimizer", "CashFlowGuard"]})
        
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        # Step 2: PaymentsOptimizer responds
        await self._log(entity_id, trace_id, "PaymentsOptimizer", "PAYMENT_HOLD",
            severity="WARNING",
            summary=f"📨 Received risk alert → Placing ₹{amount_at_risk:,} payment to {supplier} on HOLD pending review.",
            details={"triggered_by": "RiskSentinel", "supplier": supplier,
                     "action": "payment_hold", "amount_held": amount_at_risk})
        
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        # Step 3: CashFlowGuard validates impact
        new_runway_boost = random.randint(3, 8)
        await self._log(entity_id, trace_id, "CashFlowGuard", "IMPACT_ASSESSMENT",
            severity="INFO",
            summary=f"✅ Payment hold on {supplier} adds {new_runway_boost} days to runway. Cash position improved.",
            details={"triggered_by": "PaymentsOptimizer → RiskSentinel chain",
                     "runway_improvement": f"+{new_runway_boost} days",
                     "collaboration": "RiskSentinel → PaymentsOptimizer → CashFlowGuard"})

    async def _scenario_full_sweep(self, entity_id: str):
        """Supervisor orchestrates all agents for a periodic health check."""
        trace_id = f"trace-{uuid.uuid4().hex[:8]}"
        
        # Step 1: Supervisor initiates
        await self._log(entity_id, trace_id, "SupervisorAgent", "FULL_SWEEP_INITIATED",
            severity="INFO",
            summary="🔄 Initiating scheduled full-sweep analysis. Orchestrating all agents.",
            details={"agents_activated": ["CollectionsBot", "PaymentsOptimizer", "GSTComplianceAgent", 
                                          "CashFlowGuard", "RiskSentinel", "ForecastEngine"],
                     "trigger": "scheduled_30min_cycle"})
        
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        # Step 2-4: Individual reports
        agents_report = [
            ("CollectionsBot", f"DSO at {random.randint(28, 65)} days. {random.randint(0, 5)} new overdue invoices."),
            ("GSTComplianceAgent", f"GSTR-1 {'✅ filed' if random.random() > 0.3 else '⏳ pending'}. ITC: ₹{random.randint(50000, 200000):,} available."),
            ("CashFlowGuard", f"Runway: {random.randint(12, 45)} days. Burn rate: ₹{random.randint(80000, 200000):,}/day."),
        ]
        
        for agent, report in agents_report:
            await self._log(entity_id, trace_id, agent, "SWEEP_REPORT",
                severity="INFO",
                summary=f"📊 Reporting to SupervisorAgent → {report}",
                details={"reporting_to": "SupervisorAgent", "trace": trace_id})
            await asyncio.sleep(random.uniform(0.2, 0.4))
        
        # Step 5: Supervisor summary
        health = random.choice(["HEALTHY", "ATTENTION_NEEDED", "AT_RISK"])
        await self._log(entity_id, trace_id, "SupervisorAgent", "SWEEP_COMPLETE",
            severity="WARNING" if health != "HEALTHY" else "INFO",
            summary=f"📋 Full sweep complete. Overall health: **{health}**. {len(agents_report)} agents reported. All findings logged.",
            details={"health_status": health, "agents_reported": len(agents_report),
                     "collaboration": "SupervisorAgent orchestrated all agents"})

    # ======================================================================
    # HELPER
    # ======================================================================

    async def _log(self, entity_id, trace_id, agent, action, severity="INFO", summary="", details=None):
        """Write a single audit log entry with trace_id for grouping."""
        log = AuditLog(
            entity_id=entity_id,
            agent_name=agent,
            event_type="AI_AGENT",
            action=action,
            severity=severity,
            reasoning=summary,
            details=details or {},
            trace_id=trace_id
        )
        self.db.add(log)
        self.db.commit()


async def simulate_workforce():
    """Global loop for background agent simulation (for demo purposes)."""
    print("🤖 Agent Workforce background loop started")
    while True:
        db = SessionLocal()
        try:
            entities = db.query(Entity).all()
            if not entities:
                print("DEBUG: No entities found for background simulation.")
            for ent in entities:
                svc = AgentWorkforceService(db)
                await svc.run_background_cycle(ent.id)
            print(f"✅ Agent cycle completed for {len(entities)} entities at {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"❌ Workforce simulation error: {e}")
            traceback.print_exc()
        finally:
            db.close()
        
        # Run every 30 seconds
        await asyncio.sleep(30)
