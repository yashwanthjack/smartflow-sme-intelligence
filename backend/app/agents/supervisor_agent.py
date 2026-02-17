# Multi-Agent Orchestrator for SmartFlow
# Intelligent supervisor that understands queries, orchestrates multi-agent
# collaboration, and synthesizes combined answers.

import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.agents.collections_agent import run_collections_agent
from app.agents.payments_agent import run_payments_agent
from app.agents.gst_agent import run_gst_agent
from app.agents.credit_advisory_agent import run_credit_advisory_agent

# Force reload for GST agent updates


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
    # "how is my business doing" → All agents
    {
        "patterns": [r"(how|what).*(business|company|financ).*(doing|look|go|health|status|stand)",
                     r"overall.*(status|health|summary)", r"business health",
                     r"everything", r"full.*(report|analysis|check)", r"complete.*picture"],
        "agents": ["collections", "payments", "gst", "credit"],
        "type": "full_health"
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
        "agents": ["collections", "payments", "credit"],
        "type": "priority_decision"
    },
    # "am I compliant" → GST + Credit
    {
        "patterns": [r"(compliant|compliance).*(status|check|ok)", r"any.*(risk|issue|problem|pending)",
                     r"what.*(wrong|issue|problem|pending|concern)"],
        "agents": ["gst", "credit", "collections"],
        "type": "risk_check"
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
    
    # Step 4: For ANY other query — run all agents (don't say "I don't understand")
    # This ensures queries like "revenue dip when expected?" always get answered
    return {"type": "multi", "agents": ["collections", "payments", "gst", "credit"], "subtype": "full_health"}


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
• **GSTComplianceAgent** — watches your tax compliance
• **CreditAdvisoryAgent** — monitors credit & cash runway

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
# MULTI-AGENT SYNTHESIS — the core intelligence
# ======================================================================

def _synthesize_payment_priority(results: Dict[str, Any]) -> str:
    """Combine Payments + Credit data to recommend who to pay first."""
    payments_data = results.get("payments", {}).get("output", "")
    credit_data = results.get("credit", {}).get("output", "")
    
    output = """🧠 **Multi-Agent Decision: Payment Priority**
_CollectionsBot + PaymentsOptimizer + CashFlowGuard collaborated_

"""
    # Extract and present prioritized recommendation
    output += "**Step 1 — PaymentsOptimizer** analyzed your pending bills:\n"
    # Get the payables section only
    if "payable" in payments_data.lower() or "pending" in payments_data.lower():
        # Extract just the payables list
        lines = payments_data.split("\n")
        payable_lines = [l for l in lines if "₹" in l and ("due" in l.lower() or "day" in l.lower() or "overdue" in l.lower())]
        if payable_lines:
            for line in payable_lines[:5]:
                output += f"  {line.strip()}\n"
        else:
            output += f"  {payments_data[:300]}\n"
    
    output += "\n**Step 2 — CashFlowGuard** checked your cash position:\n"
    if credit_data:
        # Extract runway info
        for line in credit_data.split("\n"):
            if any(w in line.lower() for w in ["runway", "balance", "cash", "healthy", "critical"]):
                output += f"  {line.strip()}\n"
    
    output += """
**Step 3 — Combined Recommendation:**
1. 🔴 **Pay critical vendors first** — those with due dates within 3 days (avoid penalties & supply chain disruption)
2. 🟡 **Hold medium-priority payments** if cash runway is under 30 days
3. 🟢 **Negotiate extended terms** with low-priority vendors if cash is tight
4. 💡 **Collect before you pay** — accelerate overdue receivables to fund payables
"""
    return output


def _synthesize_loan_advisory(results: Dict[str, Any]) -> str:
    """Combine Credit + Payments data to advise on loans."""
    credit_data = results.get("credit", {}).get("output", "")
    payments_data = results.get("payments", {}).get("output", "")
    
    output = """🧠 **Multi-Agent Decision: Loan Advisory**
_CreditAdvisoryAgent + PaymentsOptimizer collaborated_

"""
    output += "**Step 1 — CreditAdvisoryAgent** assessed your creditworthiness:\n"
    for line in credit_data.split("\n"):
        if any(w in line.lower() for w in ["score", "band", "runway", "eligible", "lender"]):
            output += f"  {line.strip()}\n"
    
    output += "\n**Step 2 — PaymentsOptimizer** reviewed your obligations:\n"
    for line in payments_data.split("\n"):
        if any(w in line.lower() for w in ["total", "pending", "critical", "due"]):
            output += f"  {line.strip()}\n"
    
    output += """
**Step 3 — Joint Recommendation:**
• If credit score > 700: You qualify for competitive rates. Invoice discounting (10-12% p.a.) is cheaper than term loans (14-18% p.a.)
• If runway < 15 days: **Urgent** — consider emergency working capital facility
• If runway > 30 days: Focus on improving collections before borrowing
• 💡 Always compare cost of capital vs. expected return before borrowing
"""
    return output


def _synthesize_full_health(results: Dict[str, Any]) -> str:
    """Combine all agent data for a comprehensive health check."""
    output = """🧠 **Multi-Agent Health Check**
_All agents collaborated on this analysis_

"""
    sections = {
        "collections": ("📋 Collections", "CollectionsBot"),
        "payments": ("💰 Payments", "PaymentsOptimizer"),
        "gst": ("📊 GST", "GSTComplianceAgent"),
        "credit": ("📈 Credit", "CreditAdvisoryAgent"),
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
    
    # Overall assessment
    output += """---
**🎯 Top 3 Actions:**
1. Focus on highest-impact item from collections (overdue receivables)
2. Manage cash runway by prioritizing critical vendor payments
3. Stay GST compliant to avoid penalties and credit score impact
"""
    return output


def _synthesize_affordability(results: Dict[str, Any]) -> str:
    """Combine Payments + Credit data to check affordability."""
    credit_data = results.get("credit", {}).get("output", "")
    payments_data = results.get("payments", {}).get("output", "")
    
    output = """🧠 **Multi-Agent Decision: Affordability Check**
_PaymentsOptimizer + CashFlowGuard collaborated_

"""
    output += "**Cash Position:**\n"
    for line in credit_data.split("\n"):
        if any(w in line.lower() for w in ["runway", "balance", "burn", "healthy", "critical"]):
            output += f"  {line.strip()}\n"
    
    output += "\n**Pending Obligations:**\n"
    for line in payments_data.split("\n"):
        if any(w in line.lower() for w in ["total", "pending", "critical", "₹"]):
            output += f"  {line.strip()}\n"
            if len([l for l in payments_data.split("\n") if "₹" in l]) > 3:
                break
    
    output += "\n**Verdict:** "
    if "critical" in credit_data.lower() or "urgent" in credit_data.lower():
        output += "⚠️ **Not safe** to pay all vendors right now. Prioritize critical payments only."
    else:
        output += "✅ Cash position looks manageable. Pay critical vendors and schedule the rest."
    
    return output


def _synthesize_priority_decision(results: Dict[str, Any]) -> str:
    """Recommend what to focus on based on all available data."""
    output = """🧠 **Multi-Agent Decision: Today's Priorities**
_CollectionsBot + PaymentsOptimizer + CashFlowGuard collaborated_

"""
    collections = results.get("collections", {}).get("output", "")
    payments = results.get("payments", {}).get("output", "")
    credit = results.get("credit", {}).get("output", "")
    
    priorities = []
    
    # Check collections urgency
    if any(w in collections.lower() for w in ["overdue", "past due", "late"]):
        priorities.append("🔴 **Collect overdue payments** — you have outstanding receivables")
    
    # Check payment urgency
    if any(w in payments.lower() for w in ["critical", "due within", "urgent"]):
        priorities.append("🟡 **Pay critical vendors** — some bills are due soon")
    
    # Check cash urgency
    if any(w in credit.lower() for w in ["critical", "urgent", "< 15"]):
        priorities.append("🔴 **Cash running low** — extend runway immediately")
    elif "attention" in credit.lower():
        priorities.append("🟡 **Monitor cash** — runway needs attention")
    else:
        priorities.append("✅ **Cash is healthy** — focus on growth")
    
    if not priorities:
        priorities = ["✅ All systems look stable. Routine monitoring continues."]
    
    output += "**Today's Priority Stack:**\n"
    for i, p in enumerate(priorities, 1):
        output += f"{i}. {p}\n"
    
    output += "\n💡 **Tip:** Ask me specifics like \"who owes me money?\" or \"pending bills\" for details."
    return output


def _synthesize_risk_check(results: Dict[str, Any]) -> str:
    """Check for risks across all areas."""
    output = """🧠 **Multi-Agent Risk Scan**
_All agents scanned for issues_

"""
    gst = results.get("gst", {}).get("output", "")
    credit = results.get("credit", {}).get("output", "")
    collections = results.get("collections", {}).get("output", "")
    
    risks = []
    
    if any(w in gst.lower() for w in ["pending", "overdue", "non-compliant", "blocked"]):
        risks.append("⚠️ **GST**: Filing or compliance issue detected")
    if any(w in credit.lower() for w in ["critical", "low", "< 15"]):
        risks.append("🔴 **Cash**: Runway is critically low")
    if any(w in collections.lower() for w in ["overdue", "high risk", "band c"]):
        risks.append("⚠️ **Collections**: Overdue invoices / high-risk customers")
    
    if risks:
        output += "**Found these concerns:**\n"
        for r in risks:
            output += f"• {r}\n"
    else:
        output += "✅ **No major risks detected** across all areas.\n"
    
    output += "\n💡 Ask me about any specific area for details."
    return output


# Synthesis router
SYNTHESIS_MAP = {
    "payment_priority": _synthesize_payment_priority,
    "loan_advisory": _synthesize_loan_advisory,
    "full_health": _synthesize_full_health,
    "affordability": _synthesize_affordability,
    "priority_decision": _synthesize_priority_decision,
    "risk_check": _synthesize_risk_check,
}


# ======================================================================
# SUPERVISOR AGENT
# ======================================================================

class SupervisorAgent:
    """
    Intelligent orchestrator that:
    1. Understands natural language queries
    2. Routes simple queries to the right agent
    3. Orchestrates multi-agent collaboration for complex questions
    4. Synthesizes combined answers from multiple agents
    """
    
    def __init__(self):
        self.agent_runners = {
            "collections": run_collections_agent,
            "payments": run_payments_agent,
            "gst": run_gst_agent,
            "credit": run_credit_advisory_agent
        }
    
    def run(self, entity_id: str, query: str) -> Dict[str, Any]:
        """Process a user query intelligently."""
        
        intent = classify_intent(query)
        
        # --- General/conversational ---
        if intent["type"] == "general":
            return {
                "agent_used": "SmartFlow Copilot",
                "intent": "general",
                "success": True,
                "output": _handle_general_query(query, intent.get("subtype", "unknown"))
            }
        
        # --- Multi-agent collaboration ---
        if intent["type"] == "multi":
            return self._run_multi_agent(entity_id, query, intent)
        
        # --- Single agent ---
        return self._run_single_agent(entity_id, query, intent["agent"])
    
    def _run_multi_agent(self, entity_id: str, query: str, intent: Dict) -> Dict[str, Any]:
        """Orchestrate multiple agents and synthesize their outputs."""
        agents_needed = intent["agents"]
        query_type = intent["subtype"]
        
        # Step 1: Collect results from all relevant agents
        results = {}
        agents_used = []
        for agent_name in agents_needed:
            runner = self.agent_runners.get(agent_name)
            if runner:
                try:
                    result = runner(entity_id, query)
                    output = result.get("output", str(result)) if isinstance(result, dict) else str(result)
                    results[agent_name] = {"output": output, "success": True}
                    agents_used.append(agent_name)
                except Exception as e:
                    results[agent_name] = {"output": f"Error: {str(e)}", "success": False}
        
        # Step 2: Synthesize combined answer
        synthesizer = SYNTHESIS_MAP.get(query_type)
        if synthesizer:
            combined_output = synthesizer(results)
        else:
            # Fallback: concatenate
            combined_output = "🧠 **Multi-Agent Analysis**\n\n"
            for agent_name, data in results.items():
                combined_output += f"**{agent_name}:** {data['output'][:200]}\n\n"
        
        return {
            "agent_used": " + ".join(agents_used),
            "intent": query_type,
            "success": True,
            "output": combined_output
        }
    
    def _run_single_agent(self, entity_id: str, query: str, agent_name: str) -> Dict[str, Any]:
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
            result = runner(entity_id, query)
            output = result.get("output", str(result)) if isinstance(result, dict) else str(result)
            
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
    
    def run_full_analysis(self, entity_id: str) -> Dict[str, Any]:
        """Run all agents for comprehensive analysis."""
        intent = {"agents": ["collections", "payments", "gst", "credit"], "subtype": "full_health"}
        return self._run_multi_agent(entity_id, "full analysis", intent)


# Convenience functions
def run_supervisor(entity_id: str, query: str) -> Dict[str, Any]:
    supervisor = SupervisorAgent()
    return supervisor.run(entity_id, query)

def run_full_analysis(entity_id: str) -> Dict[str, Any]:
    supervisor = SupervisorAgent()
    return supervisor.run_full_analysis(entity_id)
