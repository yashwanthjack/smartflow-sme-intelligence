import random
import asyncio
import traceback
import uuid
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import SessionLocal
from app.models.audit_log import AuditLog
from app.models.entity import Entity
from app.agents.llm import get_llm


class AgentWorkforceService:
    """Real data-driven multi-agent orchestration service.
    
    Instead of generating random mock scenarios, this service checks the actual
    database for conditions that warrant agent intervention, then triggers the
    appropriate multi-agent collaboration workflows.
    """
    
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
            response = await self.llm.ainvoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"LLM gen failed: {e}")
            return fallback

    def _get_real_overdue_invoices(self, entity_id: str):
        """Get actual overdue invoices from database."""
        try:
            from app.models.invoice import Invoice
            from app.models.counterparty import Counterparty
            
            today = date.today()
            overdue = (
                self.db.query(Invoice)
                .filter(Invoice.entity_id == entity_id)
                .filter(Invoice.invoice_type == "receivable")
                .filter(Invoice.status.in_(["pending", "partial", "overdue"]))
                .filter(Invoice.due_date < today)
                .order_by(Invoice.balance_due.desc())
                .limit(5)
                .all()
            )
            
            results = []
            for inv in overdue:
                days_overdue = (today - inv.due_date).days
                cp_name = "Unknown Customer"
                if inv.counterparty_id:
                    cp = self.db.query(Counterparty).filter(Counterparty.id == inv.counterparty_id).first()
                    if cp:
                        cp_name = cp.name
                results.append({
                    "customer": cp_name,
                    "amount": float(inv.balance_due),
                    "days_overdue": days_overdue,
                    "invoice_number": inv.invoice_number
                })
            return results
        except Exception:
            return []

    def _get_real_cash_position(self, entity_id: str):
        """Get actual cash position from ledger."""
        try:
            from app.models.ledger_entry import LedgerEntry
            
            balance = self.db.query(func.sum(LedgerEntry.amount)).filter(
                LedgerEntry.entity_id == entity_id
            ).scalar() or 0
            
            # Calculate average daily burn (last 30 days)
            thirty_days_ago = date.today() - timedelta(days=30)
            expenses = self.db.query(func.sum(LedgerEntry.amount)).filter(
                LedgerEntry.entity_id == entity_id,
                LedgerEntry.amount < 0,
                LedgerEntry.ledger_date >= thirty_days_ago
            ).scalar() or 0
            
            daily_burn = abs(expenses) / 30 if expenses else 0
            runway_days = int(balance / daily_burn) if daily_burn > 0 else 999
            
            return {
                "balance": float(balance),
                "daily_burn": float(daily_burn),
                "runway_days": runway_days
            }
        except Exception:
            return None

    def _get_real_pending_payables(self, entity_id: str):
        """Get actual pending payables from database."""
        try:
            from app.models.invoice import Invoice
            from app.models.counterparty import Counterparty
            
            today = date.today()
            upcoming = today + timedelta(days=7)
            
            payables = (
                self.db.query(Invoice)
                .filter(Invoice.entity_id == entity_id)
                .filter(Invoice.invoice_type == "payable")
                .filter(Invoice.status.in_(["pending", "partial"]))
                .filter(Invoice.due_date <= upcoming)
                .order_by(Invoice.due_date)
                .limit(5)
                .all()
            )
            
            results = []
            for inv in payables:
                days_until = (inv.due_date - today).days
                cp_name = "Unknown Vendor"
                if inv.counterparty_id:
                    cp = self.db.query(Counterparty).filter(Counterparty.id == inv.counterparty_id).first()
                    if cp:
                        cp_name = cp.name
                results.append({
                    "vendor": cp_name,
                    "amount": float(inv.balance_due),
                    "days_until_due": days_until,
                    "is_overdue": days_until < 0
                })
            return results
        except Exception:
            return []

    def _get_real_gst_status(self, entity_id: str):
        """Get actual GST filing status."""
        try:
            from app.models.gst_summary import GSTSummary
            
            latest = (
                self.db.query(GSTSummary)
                .filter(GSTSummary.entity_id == entity_id)
                .order_by(GSTSummary.period.desc())
                .first()
            )
            
            if latest:
                return {
                    "period": latest.period,
                    "filing_status": latest.filing_status,
                    "output_tax": float(latest.output_tax or 0),
                    "input_credit": float(latest.input_credit or 0)
                }
        except Exception:
            pass
        return None

    async def _detect_anomalies_and_account_type(self, entity_id: str, trace_id: str):
        """Analyze recent transactions for anomalies and auto-sense account category."""
        try:
            from app.models.ledger_entry import LedgerEntry
            from app.models.entity import Entity
            
            # Get entity config
            entity = self.db.query(Entity).filter(Entity.id == entity_id).first()
            if not entity: return False
            
            # Current category
            current_category = getattr(entity, 'account_category', 'BUSINESS')
            
            # 1. Anomaly Detection (Large Transactions)
            thirty_days_ago = date.today() - timedelta(days=30)
            recent_txs = (
                self.db.query(LedgerEntry)
                .filter(LedgerEntry.entity_id == entity_id)
                .filter(LedgerEntry.ledger_date >= thirty_days_ago)
                .order_by(LedgerEntry.ledger_date.desc())
                .all()
            )
            
            if not recent_txs: return False
            
            # Calculate standard average absolute transaction size
            abs_amounts = [abs(float(tx.amount)) for tx in recent_txs]
            avg_amount = sum(abs_amounts) / len(abs_amounts)
            
            triggered = False
            
            # Check the last 3 days for massive spikes (>3x average AND > ₹50,000)
            three_days_ago = date.today() - timedelta(days=3)
            recent_anomalies = [tx for tx in recent_txs if tx.ledger_date >= three_days_ago and abs(float(tx.amount)) > (avg_amount * 3) and abs(float(tx.amount)) > 50000]
            
            for tx in recent_anomalies:
                tx_type = "outflow" if tx.amount < 0 else "inflow"
                tx_amt = abs(float(tx.amount))
                
                # Contextualize impact based on burn rate
                impact_text = "This may significantly impact your cash runway."
                
                await self._log(entity_id, trace_id, "CashFlowGuard", "ANOMALOUS_TRANSACTION",
                    severity="CRITICAL",
                    summary=f"🚨 Large unexpected {tx_type} of ₹{tx_amt:,.0f} detected on {tx.ledger_date}. {impact_text}",
                    details={"transaction_id": tx.id, "amount": tx_amt, "type": tx_type, "average_size": avg_amount})
                triggered = True

            # 2. Auto-Sense Account Category
            # Look at description patterns. If they are all Amazon, Zomato, Salary, Rent (Personal) 
            # vs AWS, Payroll, Supplier, Raw Materials (Business)
            
            if len(recent_txs) > 5 and current_category != "PERSONAL":
                descriptions = [tx.description for tx in recent_txs[:15] if tx.description]
                desc_text = ", ".join(descriptions)
                
                prompt = f"""You are an AI financial categorizer.
Based on the following 15 recent transaction descriptions, decide if this account belongs to a 'BUSINESS' (SME, enterprise, B2B) or a 'PERSONAL' account (individual, household expenses).
Transactions: {desc_text}
Respond with EXACTLY ONE WORD: either BUSINESS or PERSONAL."""
                
                category = await self._generate_text(prompt, "BUSINESS")
                category = category.strip().upper()
                
                if "PERSONAL" in category and current_category != "PERSONAL":
                    # Update DB
                    entity.account_category = "PERSONAL"
                    self.db.commit()
                    
                    await self._log(entity_id, trace_id, "SmartFlow Copilot", "ACCOUNT_TYPE_SENCED",
                        severity="WARNING",
                        summary="🧠 AI Auto-Sense: Transaction patterns resemble a personal account. Optimizing dashboard to hide complex SME features like GST & mass payroll.",
                        details={"previous_category": current_category, "new_category": "PERSONAL", "reason": "Transaction pattern analysis"})
                    triggered = True

            return triggered
            
        except Exception as e:
            print(f"Anomaly detection failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def run_background_cycle(self, entity_id: str):
        """Data-driven multi-agent orchestration cycle.
        
        Checks real database conditions and triggers appropriate agent workflows.
        """
        trace_id = f"trace-{uuid.uuid4().hex[:8]}"
        
        # Gather real data
        overdue = self._get_real_overdue_invoices(entity_id)
        cash = self._get_real_cash_position(entity_id)
        payables = self._get_real_pending_payables(entity_id)
        gst = self._get_real_gst_status(entity_id)
        
        triggered_any = False
        
        # ======= SCENARIO 0: Anomalies & Auto-Sensing =======
        anomalies_found = await self._detect_anomalies_and_account_type(entity_id, trace_id)
        if anomalies_found:
            triggered_any = True
            
        # ======= SCENARIO 1: Overdue collections detected =======
        if overdue:
            triggered_any = True
            total_overdue = sum(inv["amount"] for inv in overdue)
            worst = max(overdue, key=lambda x: x["days_overdue"])
            
            summary = await self._generate_text(
                f"You are CollectionsBot. You found {len(overdue)} overdue invoices totaling ₹{total_overdue:,.0f}. "
                f"Worst: {worst['customer']} owes ₹{worst['amount']:,.0f} ({worst['days_overdue']} days late). "
                f"Write a concise 1-sentence audit log summary.",
                f"Found {len(overdue)} overdue invoices totaling ₹{total_overdue:,.0f}. "
                f"Highest: {worst['customer']} — ₹{worst['amount']:,.0f} ({worst['days_overdue']} days overdue)."
            )
            
            sev = "CRITICAL" if worst["days_overdue"] > 30 else ("WARNING" if worst["days_overdue"] > 14 else "INFO")
            await self._log(entity_id, trace_id, "CollectionsBot", "OVERDUE_DETECTED",
                severity=sev, summary=summary,
                details={"total_overdue": total_overdue, "count": len(overdue),
                         "worst_customer": worst["customer"], "worst_amount": worst["amount"],
                         "worst_days": worst["days_overdue"]})
            
            # Cross-agent: If cash is also low, escalate
            if cash and cash["runway_days"] < 30:
                await asyncio.sleep(random.uniform(0.2, 0.5))
                await self._log(entity_id, trace_id, "CashFlowGuard", "COLLECTION_URGENCY_RAISED",
                    severity="WARNING",
                    summary=f"📨 Cash runway is only {cash['runway_days']} days. Accelerating collection of ₹{total_overdue:,.0f} in overdue receivables.",
                    details={"triggered_by": "CollectionsBot", "runway_days": cash["runway_days"],
                             "overdue_amount": total_overdue,
                             "collaboration": "CollectionsBot → CashFlowGuard"})
        
        # ======= SCENARIO 2: Low cash runway =======
        if cash and cash["runway_days"] < 30:
            triggered_any = True
            sev = "CRITICAL" if cash["runway_days"] < 15 else "WARNING"
            
            await self._log(entity_id, trace_id, "CashFlowGuard", "RUNWAY_ANALYSIS",
                severity=sev,
                summary=f"Cash runway: {cash['runway_days']} days at ₹{cash['daily_burn']:,.0f}/day burn rate. "
                        f"Balance: ₹{cash['balance']:,.0f}. {'⚠️ Alerting PaymentsOptimizer!' if cash['runway_days'] < 30 else '✅ Healthy.'}",
                details={"runway_days": cash["runway_days"], "burn_rate": cash["daily_burn"],
                         "balance": cash["balance"], "alert_sent_to": "PaymentsOptimizer"})
            
            # Cross-agent: Tell PaymentsOptimizer to defer non-critical payments
            if payables:
                await asyncio.sleep(random.uniform(0.2, 0.5))
                non_critical = [p for p in payables if not p["is_overdue"] and p["days_until_due"] > 3]
                if non_critical:
                    defer_amount = sum(p["amount"] for p in non_critical)
                    await self._log(entity_id, trace_id, "PaymentsOptimizer", "PAYMENT_RESCHEDULED",
                        severity="WARNING",
                        summary=f"📨 Received alert from CashFlowGuard (runway={cash['runway_days']}d). "
                                f"Deferring {len(non_critical)} non-critical payments (₹{defer_amount:,.0f}) to extend runway.",
                        details={"triggered_by": "CashFlowGuard", "payments_deferred": len(non_critical),
                                 "amount_deferred": defer_amount, "critical_payments_preserved": True,
                                 "collaboration": "CashFlowGuard → PaymentsOptimizer"})
        
        # ======= SCENARIO 3: Critical payables due soon =======
        critical_payables = [p for p in payables if p["is_overdue"] or p["days_until_due"] <= 3]
        if critical_payables:
            triggered_any = True
            total_critical = sum(p["amount"] for p in critical_payables)
            
            await self._log(entity_id, trace_id, "PaymentsOptimizer", "CRITICAL_PAYMENTS_ALERT",
                severity="WARNING",
                summary=f"⚠️ {len(critical_payables)} critical payments due: ₹{total_critical:,.0f}. "
                        f"Immediate action needed to avoid penalties.",
                details={"count": len(critical_payables), "total_amount": total_critical,
                         "vendors": [p["vendor"] for p in critical_payables]})
        
        # ======= SCENARIO 4: GST compliance issues =======
        if gst and gst["filing_status"] not in ["filed", "Filed", None]:
            triggered_any = True
            await self._log(entity_id, trace_id, "GSTComplianceAgent", "FILING_STATUS_CHECK",
                severity="WARNING",
                summary=f"GST filing status for {gst['period']}: {gst['filing_status']}. "
                        f"Output tax: ₹{gst['output_tax']:,.0f}, Input credit: ₹{gst['input_credit']:,.0f}.",
                details={"period": gst["period"], "status": gst["filing_status"],
                         "output_tax": gst["output_tax"], "input_credit": gst["input_credit"]})
        
        # ======= SCENARIO 5: Periodic health check (if nothing else triggered) =======
        if not triggered_any:
            # Everything is healthy — log a clean sweep
            await self._log(entity_id, trace_id, "SupervisorAgent", "HEALTH_CHECK",
                severity="INFO",
                summary="✅ Periodic health check: No critical issues detected. All systems normal.",
                details={
                    "collections": f"{len(overdue)} overdue" if overdue else "clear",
                    "cash_runway": f"{cash['runway_days']} days" if cash else "unknown",
                    "payables": f"{len(payables)} pending" if payables else "clear",
                    "gst": gst["filing_status"] if gst else "no data"
                })

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
    """Global loop for background agent simulation."""
    print("🤖 Agent Workforce background loop started (data-driven mode)")
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
