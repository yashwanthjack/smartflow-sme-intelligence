# Multi-Agent Orchestrator for SmartFlow
# Intelligent supervisor that understands queries, orchestrates multi-agent
# collaboration, and uses LLM to synthesize combined answers.

import re
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
import json
from app.agents.collections_agent import run_collections_agent
from app.agents.payments_agent import run_payments_agent
from app.agents.gst_agent import run_gst_agent
from app.agents.credit_advisory_agent import run_credit_advisory_agent
from app.agents.decision_advisor_agent import run_decision_advisor_agent
from app.db.database import SessionLocal
from app.models.audit_log import AuditLog


# ======================================================================
# INTENT CLASSIFICATION
# ======================================================================

AGENT_KEYWORDS = {
    "collections": [
        "overdue", "receivable", "dso", "collection", "reminder", "invoice due",
        "customer payment", "outstanding", "aging", "past due", "unpaid",
        "follow up", "late payment", "defaulter", "owed to me", "owes me",
        "who owes", "collect"
    ],
    "payments": [
        "payable", "dpo", "vendor", "supplier", "pay", "payment",
        "schedule payment", "pending payment", "bill", "payment due",
        "vendor payment", "outgoing", "pay first", "pay whom", "whom to pay",
        "who to pay", "expenses", "spend"
    ],
    "gst": [
        "gst", "gstr", "itc", "input tax", "compliance", "filing", "tax credit",
        "reconciliation", "gstr-1", "gstr-3b", "gstr-2a", "gstr-2b",
        "tax return", "tax filing", "tax"
    ],
    "credit": [
        "credit", "score", "loan", "eligibility", "lender", "working capital",
        "credit rating", "creditworthiness", "financing", "runway",
        "cash runway", "burn rate", "financial health", "cash position",
        "how long", "months left", "survive", "revenue", "forecast",
        "predict", "projection", "dip", "expected", "trend", "growth",
        "decline", "revenue dip", "sales forecast", "income", "earning",
        "next month", "next quarter", "when", "future", "cashflow", 
        "cash flow", "balance prediction", "future balance"
    ]
}

# General/conversational patterns — handle WITHOUT dumping financial data
GENERAL_PATTERNS = [
    (r"\b(hi|hello|hey|good morning|good evening|namaste|howdy)\b", "greeting"),
    (r"\b(what time|whats the time|current time|time now|what's the time)\b", "time"),
    (r"\b(who are you|what are you|your name|about you|what can you do)\b", "identity"),
    (r"\b(thank|thanks|thx|appreciate)\b", "thanks"),
    (r"\b(help|how to use|guide|tutorial)\b", "help"),
    (r"\b(bye|goodbye|see you|quit|exit)\b", "farewell"),
]

# Complex queries requiring MULTIPLE agents to collaborate
MULTI_AGENT_PATTERNS = [
    # "from whom i got the highest" → Direct answer from ledger
    {
        "patterns": [r"from whom.*(got|received).*highest", r"who.*gave.*highest", r"highest.*(received|got).*from",
                     r"biggest.*payment.*from", r"largest.*income.*from"],
        "agents": [],  # Special case - direct tool call
        "type": "highest_received"
    },
    # "who should I pay first" → Payments + CashFlow + Risk
    {
        "patterns": [r"pay first", r"pay whom", r"whom.*(to|should).*pay", r"who.*(to|should|need).*pay",
                     r"priorit.*(pay|vendor|bill)", r"which bill", r"urgent.*(pay|bill)"],
        "agents": ["payments", "credit"],
        "type": "payment_priority"
    },
    # "should I take a loan" → Credit + CashFlow
    {
        "patterns": [r"should.*(loan|borrow|financ)", r"need.*(loan|money|fund)",
                     r"can i.*(borrow|get.*loan|afford)", r"take.*(loan|credit)"],
        "agents": ["credit", "payments"],
        "type": "loan_advisory"
    },
    # "how is my business doing" → Core agents
    {
        "patterns": [r"(how|what).*(business|company|financ).*(doing|look|go|health|status|stand)",
                     r"overall.*(status|health|summary)", r"business health",
                     r"everything", r"full.*(report|analysis|check)", r"complete.*picture"],
        "agents": ["collections", "payments"],
        "type": "core_health"
    },
    # "am I safe to pay / can I afford" → Payments + CashFlow
    {
        "patterns": [r"(safe|afford|can i).*(pay|spend|invest)", r"enough.*(money|cash|fund)",
                     r"(risk|danger).*(pay|spend)"],
        "agents": ["payments", "credit"],
        "type": "affordability"
    },
    # "collect or pay" / priority decisions
    {
        "patterns": [r"collect.*or.*pay", r"pay.*or.*collect", r"what.*should.*focus",
                     r"priority.*today", r"most.*important", r"what.*next", r"action.*(item|plan)"],
        "agents": ["collections", "payments"],
        "type": "priority_decision"
    },
    # "am I compliant" → Core agents
    {
        "patterns": [r"(compliant|compliance).*(status|check|ok)", r"any.*(risk|issue|problem|pending)",
                     r"what.*(wrong|issue|problem|pending|concern)"],
        "agents": ["collections", "payments", "gst"],
        "type": "risk_check"
    },
    # "can I hire / strategic decisions" → Decision Advisor
    {
        "patterns": [r"can i.*(hire|invest|buy|spend|afford)", r"should i.*(hire|invest|buy|spend|afford)",
                     r"impact.*of.*(hiring|investing|expense)", r"strategic.*advice"],
        "agents": ["decision_advisor", "credit"],
        "type": "strategic_decision"
    },
]


def classify_intent(query: str) -> Dict[str, Any]:
    """
    Simple classification: 
    1. Filter out greetings/conversational → handle directly
    2. Everything else → multi-agent collaboration (let the data answer)
    
    Keywords are used as HINTS to pick the best synthesis pattern,
    NOT as gatekeepers. Any financial query gets answered.
    """
    query_lower = query.lower().strip()
    
    # Step 1: Only filter out clearly conversational queries
    for pattern, intent_type in GENERAL_PATTERNS:
        if re.search(pattern, query_lower):
            return {"type": "general", "subtype": intent_type}

    # Step 1b: Direct factual queries (single-sentence response)
    if re.search(r"(highest|biggest|largest).*(transaction|txn|payment)", query_lower):
        if "received" in query_lower or "got" in query_lower or "income" in query_lower:
             return {"type": "multi", "agents": ["payments"], "subtype": "highest_received"}
        return {"type": "multi", "agents": ["payments"], "subtype": "highest_transaction"}

    # Step 2: Check if a specific multi-agent synthesis pattern matches
    for mp in MULTI_AGENT_PATTERNS:
        for pattern in mp["patterns"]:
            if re.search(pattern, query_lower):
                return {"type": "multi", "agents": mp["agents"], "subtype": mp["type"]}
    
    # Step 3: Score agents to find the BEST single-agent match (if any strongly matches)
    scores = {}
    for agent, keywords in AGENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        scores[agent] = score
    
    best_agent = max(scores, key=scores.get)
    
    # If a strong single-agent match exists (2+ keywords), route specifically
    if scores[best_agent] >= 2:
        return {"type": "single", "agent": best_agent}
    
    # Step 4: For ANY other query — run core agents (collections and payments)
    return {"type": "multi", "agents": ["collections", "payments"], "subtype": "core_health"}


# ======================================================================
# GENERAL QUERY HANDLER
# ======================================================================

def _handle_general_query(query: str, subtype: str = "unknown") -> str:
    now = datetime.now()
    
    if subtype == "time":
        return f"🕐 It's **{now.strftime('%I:%M %p')}** on {now.strftime('%d %b %Y')}."
    
    if subtype == "greeting":
        hour = now.hour
        g = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")
        return f"""👋 {g}! I'm your SmartFlow Copilot.

Ask me things like:
• "Who should I pay first?"
• "What's my cash runway?"
• "How is my business doing?"
• "Am I GST compliant?"
• "Should I take a loan?"

I'll coordinate my agents to give you the best answer!"""

    if subtype == "identity":
        return """🤖 I'm the **SmartFlow Copilot** — your AI financial brain.

I coordinate multiple specialist agents that talk to each other:
• **CollectionsBot** — tracks who owes you money
• **PaymentsOptimizer** — manages what you owe

For complex questions, I make them collaborate. Try: "Who should I pay first?" or "How is my business doing?" """

    if subtype == "thanks":
        return "😊 You're welcome! Ask anytime."
    if subtype == "farewell":
        return "👋 See you! Agents are still monitoring in the background."
    if subtype == "help":
        return """💡 **Try asking me:**
• "Who should I pay first?" — agents collaborate to prioritize
• "Am I safe to pay all vendors?" — checks cash + payables
• "What are my biggest risks?" — scans all areas
• "How is my business doing?" — full multi-agent health check
• "Cash runway 6 months" — specific time projections"""

    return """🤔 I didn't catch that. Try asking me:
• "Who should I pay first?"
• "What's my cash runway?"
• "Any overdue invoices?"
• "How is my business doing?"
"""


# ======================================================================
# LLM-POWERED MULTI-AGENT SYNTHESIS
# ======================================================================

async def _llm_synthesize(query: str, query_type: str, results: Dict[str, Any]) -> str:
    """Use Qwen3:8b LLM to synthesize multi-agent outputs into a cohesive answer.
    
    Instead of hardcoded string concatenation, the LLM reads all agent outputs
    and generates an intelligent, context-aware combined recommendation.
    """
    from app.agents.llm import get_llm
    
    # Build the context from all agent outputs
    agent_outputs = ""
    for agent_name, data in results.items():
        output = data.get("output", "No data available")
        agent_outputs += f"\n--- {agent_name.upper()} AGENT REPORT ---\n{output}\n"
    
    synthesis_prompt = f"""You are the SmartFlow Supervisor — an intelligent orchestrator coordinating multiple financial AI agents.

The user asked: "{query}"
Query type: {query_type}

The following specialist agents have analyzed the data and provided their reports:
{agent_outputs}

YOUR TASK:
1. Read all the agent reports above carefully
2. Synthesize a unified, actionable recommendation that directly answers the user's question
3. Highlight the most critical findings across agents
4. Provide a clear "Top 3 Actions" list at the end
5. Use emojis and markdown formatting for readability

IMPORTANT:
- Do NOT simply repeat each agent's output
- Cross-reference data between agents (e.g., if runway is low AND there are overdue invoices, connect these)
- If the Decision Advisor provided a simulation, highlight the old vs new runway
- Be specific with numbers (₹ amounts, days, percentages)
- Keep the response concise but comprehensive
- Start with "🧠 **Multi-Agent Analysis**" header

Synthesize now:"""
    
    try:
        llm = get_llm()
        response = await llm.ainvoke(synthesis_prompt)
        output = response.content if hasattr(response, 'content') else str(response)
        return output
    except Exception as e:
        print(f"⚠️ LLM synthesis failed: {e}, using fallback")
        return _fallback_synthesis(query_type, results)


def _fallback_synthesis(query_type: str, results: Dict[str, Any]) -> str:
    """Fallback synthesis when LLM is unavailable — structured template-based output."""
    output = "🧠 **Multi-Agent Analysis**\n_All agents collaborated on this analysis_\n\n"
    
    sections = {
        "collections": ("📋 Collections", "CollectionsBot"),
        "payments": ("💰 Payments", "PaymentsOptimizer"),
    }
    
    for agent, (emoji, name) in sections.items():
        data = results.get(agent, {}).get("output", "Data unavailable")
        # Extract key metrics only (first 3 meaningful lines)
        key_lines = []
        for line in data.split("\n"):
            line = line.strip()
            if line and not line.startswith("**Recommend") and not line.startswith("---") and "Agent" not in line and len(line) > 5:
                key_lines.append(line)
            if len(key_lines) >= 3:
                break
        
        output += f"**{emoji} {name}:**\n"
        for kl in key_lines:
            output += f"  {kl}\n"
        output += "\n"
    
    output += """---
**🎯 Top 3 Actions:**
1. Focus on highest-impact item from collections (overdue receivables)
2. Manage cash runway by prioritizing critical vendor payments
3. Stay GST compliant to avoid penalties and credit score impact
"""
    return output


# ======================================================================
# SUPERVISOR AGENT
# ======================================================================

class SupervisorAgent:
    """
    Intelligent orchestrator that:
    1. Understands natural language queries
    2. Routes simple queries to the right agent
    3. Orchestrates multi-agent collaboration for complex questions
    4. Uses LLM to synthesize combined answers from multiple agents
    """
    
    def __init__(self):
        self.agent_runners = {
            "collections": run_collections_agent,
            "payments": run_payments_agent,
            "gst": run_gst_agent,
            "credit": run_credit_advisory_agent,
            "decision_advisor": run_decision_advisor_agent,
        }
    
    async def run(self, entity_id: str, query: str) -> Dict[str, Any]:
        """Process a user query intelligently."""
        
        intent = classify_intent(query)
        
        # --- General/conversational ---
        if intent["type"] == "general":
            output = _handle_general_query(query, intent.get("subtype", "unknown"))
            self._log_interaction(entity_id, "SmartFlow Copilot", "GENERAL_QUERY", "INFO", "Responded to general query.", query)
            return {
                "agent_used": "SmartFlow Copilot",
                "intent": "general",
                "success": True,
                "output": output
            }
        
        # --- Special direct queries ---
        if intent["type"] == "multi" and intent["subtype"] == "highest_received":
            from app.agents.tools import get_highest_received_payment
            output = get_highest_received_payment.invoke({"entity_id": entity_id})
            self._log_interaction(entity_id, "SupervisorAgent", "DIRECT_TOOL", "INFO", f"Answered direct query: '{query}'", output)
            return {
                "agent_used": "Direct Tool",
                "intent": "highest_received",
                "success": True,
                "output": output
            }

        if intent["type"] == "multi" and intent["subtype"] == "highest_transaction":
            from app.agents.tools import get_highest_transaction
            output = get_highest_transaction.invoke({"entity_id": entity_id})
            self._log_interaction(entity_id, "SupervisorAgent", "DIRECT_TOOL", "INFO", f"Answered direct query: '{query}'", output)
            return {
                "agent_used": "Direct Tool",
                "intent": "highest_transaction",
                "success": True,
                "output": output
            }

        # --- Multi-agent collaboration ---
        if intent["type"] == "multi":
            return await self._run_multi_agent(entity_id, query, intent)
        
        # --- Single agent ---
        return await self._run_single_agent(entity_id, query, intent["agent"])
    
    async def _run_multi_agent(self, entity_id: str, query: str, intent: Dict) -> Dict[str, Any]:
        """Orchestrate multiple agents and use LLM to synthesize their outputs."""
        agents_needed = intent["agents"]
        query_type = intent["subtype"]
        
        # Step 1: Collect results from all relevant agents
        results = {}
        agents_used = []
        for agent_name in agents_needed:
            runner = self.agent_runners.get(agent_name)
            if runner:
                try:
                    result = await runner(entity_id, query)
                    output = result.get("output", str(result)) if isinstance(result, dict) else str(result)
                    results[agent_name] = {"output": output, "success": True}
                    agents_used.append(agent_name)
                except Exception as e:
                    results[agent_name] = {"output": f"Error: {str(e)}", "success": False}
        
        # Step 2: LLM-powered synthesis (upgraded from hardcoded templates)
        combined_output = await _llm_synthesize(query, query_type, results)
        
        agent_used_str = " + ".join(agents_used)
        
        self._log_interaction(
            entity_id, 
            "SupervisorAgent", 
            "MULTI_AGENT_SYNTHESIS", 
            "INFO", 
            f"Coordinated {len(agents_used)} agents ({agent_used_str}) to answer: '{query}'",
            combined_output
        )
        
        return {
            "agent_used": agent_used_str,
            "intent": query_type,
            "success": True,
            "output": combined_output
        }
    
    async def _run_single_agent(self, entity_id: str, query: str, agent_name: str) -> Dict[str, Any]:
        """Route to a single agent."""
        runner = self.agent_runners.get(agent_name)
        
        if runner is None:
            return {
                "agent_used": "none",
                "intent": agent_name,
                "success": False,
                "output": _handle_general_query(query, "unknown")
            }
        
        try:
            result = await runner(entity_id, query)
            output = result.get("output", str(result)) if isinstance(result, dict) else str(result)
            
            self._log_interaction(
                entity_id, 
                agent_name, 
                "DIRECT_QUERY", 
                "INFO", 
                f"Handled direct query: '{query}'",
                output
            )
            
            return {
                "agent_used": agent_name,
                "intent": agent_name,
                "success": True,
                "output": output
            }
        except Exception as e:
            return {
                "agent_used": agent_name,
                "intent": agent_name,
                "success": False,
                "error": str(e),
                "fallback_output": f"⚠️ {agent_name} encountered an error. Please try again."
            }
    
    async def run_full_analysis(self, entity_id: str) -> Dict[str, Any]:
        """Run core agents for comprehensive analysis."""
        intent = {"agents": ["collections", "payments"], "subtype": "core_health"}
        return await self._run_multi_agent(entity_id, "full analysis", intent)

    def _log_interaction(self, entity_id: str, agent_name: str, action: str, severity: str, summary: str, details: str):
        """Log the interaction to the database for the activity feed."""
        try:
            db = SessionLocal()
            log = AuditLog(
                agent_name=agent_name,
                event_type="AI_INTERACTION",
                action=action,
                severity=severity,
                entity_id=entity_id,
                details=json.dumps({"query_or_output": details}),
                reasoning=summary,
                trace_id=f"trace-{uuid.uuid4().hex[:8]}"
            )
            db.add(log)
            db.commit()
        except Exception as e:
            print(f"Failed to log interaction: {e}")
        finally:
            if 'db' in locals():
                db.close()


# Convenience functions
async def run_supervisor(entity_id: str, query: str) -> Dict[str, Any]:
    from app.agents.tools import set_db_session
    from app.db.database import SessionLocal
    
    db = SessionLocal()
    set_db_session(db)
    
    try:
        supervisor = SupervisorAgent()
        return await supervisor.run(entity_id, query)
    finally:
        db.close()

async def run_full_analysis(entity_id: str) -> Dict[str, Any]:
    supervisor = SupervisorAgent()
    return await supervisor.run_full_analysis(entity_id)
