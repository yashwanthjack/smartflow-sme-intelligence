# Multi-Agent Orchestrator for SmartFlow
# Supervisor agent that routes requests to specialized agents

from typing import Dict, Any, List, Literal, Optional
from langchain.tools import tool
from app.agents.llm import get_llm
from app.agents.collections_agent import run_collections_agent
from app.agents.payments_agent import run_payments_agent
from app.agents.gst_agent import run_gst_agent
from app.agents.credit_advisory_agent import run_credit_advisory_agent


# Agent routing keywords
AGENT_KEYWORDS = {
    "collections": [
        "overdue", "receivable", "dso", "collection", "reminder", "invoice due",
        "customer payment", "outstanding", "aging", "past due"
    ],
    "payments": [
        "payable", "dpo", "vendor", "supplier", "pay", "cash flow", "forecast",
        "schedule payment", "pending payment", "bill"
    ],
    "gst": [
        "gst", "gstr", "itc", "input tax", "compliance", "filing", "tax credit",
        "reconciliation", "gstr-1", "gstr-3b", "gstr-2a", "gstr-2b"
    ],
    "credit": [
        "credit", "score", "loan", "eligibility", "risk", "lender", "working capital",
        "credit rating", "creditworthiness", "financing"
    ]
}


def classify_intent(query: str) -> str:
    """
    Classify user query to determine which agent should handle it.
    Returns: 'collections', 'payments', 'gst', 'credit', or 'general'
    """
    query_lower = query.lower()
    
    scores = {}
    for agent, keywords in AGENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        scores[agent] = score
    
    # Find agent with highest score
    best_agent = max(scores, key=scores.get)
    if scores[best_agent] > 0:
        return best_agent
    
    # Default to general/collections for unclassified queries
    return "collections"


@tool
def route_to_collections(entity_id: str, task: str) -> str:
    """Route request to Collections Agent for DSO and receivables management."""
    return run_collections_agent(entity_id, task)


@tool
def route_to_payments(entity_id: str, task: str) -> str:
    """Route request to Payments Agent for DPO and payables optimization."""
    return run_payments_agent(entity_id, task)


@tool
def route_to_gst(entity_id: str, task: str) -> str:
    """Route request to GST Agent for compliance and ITC management."""
    return run_gst_agent(entity_id, task)


@tool
def route_to_credit(entity_id: str, task: str) -> str:
    """Route request to Credit Advisory Agent for scoring and loan eligibility."""
    return run_credit_advisory_agent(entity_id, task)


class SupervisorAgent:
    """
    Orchestrates multiple specialized agents.
    Routes requests to the appropriate agent based on intent classification.
    Can also coordinate multi-agent workflows.
    """
    
    def __init__(self):
        self.agent_runners = {
            "collections": run_collections_agent,
            "payments": run_payments_agent,
            "gst": run_gst_agent,
            "credit": run_credit_advisory_agent
        }
    
    def run(self, entity_id: str, query: str) -> Dict[str, Any]:
        """
        Process a user query by routing to the appropriate agent.
        
        Returns:
            dict with agent_used, intent, and response
        """
        # Classify the intent
        intent = classify_intent(query)
        
        # Get the appropriate agent runner
        runner = self.agent_runners.get(intent)
        
        if runner is None:
            return {
                "agent_used": "none",
                "intent": intent,
                "success": False,
                "error": f"No agent found for intent: {intent}"
            }
        
        try:
            # Run the agent
            result = runner(entity_id, query)
            return {
                "agent_used": intent,
                "intent": intent,
                "success": True,
                "output": result
            }
        except Exception as e:
            error_msg = str(e)
            
            # Check for rate limit
            if "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                return {
                    "agent_used": intent,
                    "intent": intent,
                    "success": False,
                    "error": "AI service rate limited. Using fallback response.",
                    "fallback_output": self._get_fallback_response(intent, entity_id)
                }
            
            return {
                "agent_used": intent,
                "intent": intent,
                "success": False,
                "error": error_msg
            }
    
    def run_full_analysis(self, entity_id: str) -> Dict[str, Any]:
        """
        Run all agents to provide a comprehensive financial analysis.
        
        Returns:
            dict with results from all agents
        """
        results = {}
        
        tasks = {
            "collections": f"Analyze overdue receivables and collections status for entity {entity_id}",
            "payments": f"Analyze pending payables and cash flow for entity {entity_id}",
            "gst": f"Check GST compliance and ITC status for entity {entity_id}",
            "credit": f"Provide credit score assessment for entity {entity_id}"
        }
        
        for agent, task in tasks.items():
            try:
                runner = self.agent_runners[agent]
                results[agent] = {
                    "success": True,
                    "output": runner(entity_id, task)
                }
            except Exception as e:
                results[agent] = {
                    "success": False,
                    "error": str(e),
                    "fallback_output": self._get_fallback_response(agent, entity_id)
                }
        
        return {
            "entity_id": entity_id,
            "analysis_type": "full",
            "results": results
        }
    
    def _get_fallback_response(self, intent: str, entity_id: str) -> str:
        """Provide fallback responses when LLM is unavailable."""
        fallbacks = {
            "collections": """📋 **Collections Summary** (Fallback Mode)
                
Based on available data:
- 3 invoices are overdue (₹1.5L total)
- Oldest overdue: 30 days
- Priority: Follow up with ABC Corp (₹50K overdue)

Recommendation: Send payment reminders to overdue customers.""",

            "payments": """💰 **Payments Summary** (Fallback Mode)

Based on available data:
- 4 pending payables (₹2.65L total)
- Critical: Raw Materials Co (₹1.2L due in 5 days)
- Cash runway: 18 days at current burn rate

Recommendation: Delay non-critical payments to optimize cash flow.""",

            "gst": """📊 **GST Compliance** (Fallback Mode)

Filing Status:
- GSTR-1 (Sep 2025): Pending
- GSTR-3B (Aug 2025): Filed

ITC Summary:
- Available: ₹1.25L
- Blocked: ₹12K (Vendor non-compliance)

Recommendation: File GSTR-1 before 11th to avoid penalties.""",

            "credit": """📈 **Credit Score** (Fallback Mode)

Score: 695 / 900 (Band B - Medium Risk)

Key Factors:
✅ Stable cash flow
✅ Good collections (DSO < 45)
⚠️ High customer concentration

Loan Eligibility: ₹112.5L @ 12-15% p.a."""
        }
        
        return fallbacks.get(intent, "Data unavailable. Please try again later.")


# Convenience function
def run_supervisor(entity_id: str, query: str) -> Dict[str, Any]:
    """Run the supervisor agent on a query."""
    supervisor = SupervisorAgent()
    return supervisor.run(entity_id, query)


def run_full_analysis(entity_id: str) -> Dict[str, Any]:
    """Run comprehensive analysis across all agents."""
    supervisor = SupervisorAgent()
    return supervisor.run_full_analysis(entity_id)
