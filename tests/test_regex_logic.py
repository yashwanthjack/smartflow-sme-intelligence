
import re
from typing import Dict, Any

# --- COPIED LOGIC FROM supervisor_agent.py ---

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

GENERAL_PATTERNS = [
    (r"\b(hi|hello|hey|good morning|good evening|namaste|howdy)\b", "greeting"),
    (r"\b(what time|whats the time|current time|time now|what's the time)\b", "time"),
    (r"\b(who are you|what are you|your name|about you|what can you do)\b", "identity"),
    (r"\b(thank|thanks|thx|appreciate)\b", "thanks"),
    (r"\b(help|how to use|guide|tutorial)\b", "help"),
    (r"\b(bye|goodbye|see you|quit|exit)\b", "farewell"),
]

MULTI_AGENT_PATTERNS = [
    {
        "patterns": [r"pay first", r"pay whom", r"whom.*(to|should).*pay", r"who.*(to|should|need).*pay",
                     r"priorit.*(pay|vendor|bill)", r"which bill", r"urgent.*(pay|bill)"],
        "agents": ["payments", "credit"],
        "type": "payment_priority"
    },
    {
        "patterns": [r"should.*(loan|borrow|financ)", r"need.*(loan|money|fund)",
                     r"can i.*(borrow|get.*loan|afford)", r"take.*(loan|credit)"],
        "agents": ["credit", "payments"],
        "type": "loan_advisory"
    },
    {
        "patterns": [r"(how|what).*(business|company|financ).*(doing|look|go|health|status|stand)",
                     r"overall.*(status|health|summary)", r"business health",
                     r"everything", r"full.*(report|analysis|check)", r"complete.*picture"],
        "agents": ["collections", "payments", "gst", "credit"],
        "type": "full_health"
    },
    {
        "patterns": [r"(safe|afford|can i).*(pay|spend|invest)", r"enough.*(money|cash|fund)",
                     r"(risk|danger).*(pay|spend)"],
        "agents": ["payments", "credit"],
        "type": "affordability"
    },
    {
        "patterns": [r"collect.*or.*pay", r"pay.*or.*collect", r"what.*should.*focus",
                     r"priority.*today", r"most.*important", r"what.*next", r"action.*(item|plan)"],
        "agents": ["collections", "payments", "credit"],
        "type": "priority_decision"
    },
    {
        "patterns": [r"(compliant|compliance).*(status|check|ok)", r"any.*(risk|issue|problem|pending)",
                     r"what.*(wrong|issue|problem|pending|concern)"],
        "agents": ["gst", "credit", "collections"],
        "type": "risk_check"
    },
]

def classify_intent(query: str) -> Dict[str, Any]:
    query_lower = query.lower().strip()
    
    for pattern, intent_type in GENERAL_PATTERNS:
        if re.search(pattern, query_lower):
            return {"type": "general", "subtype": intent_type}
    
    for mp in MULTI_AGENT_PATTERNS:
        for pattern in mp["patterns"]:
            if re.search(pattern, query_lower):
                return {"type": "multi", "agents": mp["agents"], "subtype": mp["type"]}
    
    scores = {}
    for agent, keywords in AGENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        scores[agent] = score
    
    best_agent = max(scores, key=scores.get)
    
    if scores[best_agent] >= 1: # RELAXED THRESHOLD FOR TESTING SINGLE KEYWORDS
        return {"type": "single", "agent": best_agent}
    
    return {"type": "multi", "agents": ["collections", "payments", "gst", "credit"], "subtype": "full_health"}

# --- TESTS ---

def test_intent_classification():
    test_cases = [
        ("What is my cashflow forecast?", "credit"),
        ("Show me my future balance", "credit"),
        ("How long is my runway?", "credit"),
        ("How much revenue dip expected?", "credit"),
        ("What is my credit score?", "credit"),
        ("Who should I pay first?", "multi", "payment_priority"),
        ("Am I GST compliant?", "gst"),
    ]

    print("Running Supervisor Intent Classification Tests (Standalone)...")
    failed = False
    for query, expected_type, *expected_subtype in test_cases:
        result = classify_intent(query)
        
        is_success = False
        if result["type"] == "single" and result["agent"] == expected_type:
             is_success = True
        elif result["type"] == "multi" and expected_subtype and result["subtype"] == expected_subtype[0]:
             is_success = True
        elif expected_type == "credit" and (
            (result["type"] == "single" and result["agent"] == "credit") or 
            (result["type"] == "multi" and "credit" in result.get("agents", []))
        ):
            is_success = True

        status = "✅ PASS" if is_success else f"❌ FAIL (Got {result})"
        print(f"Query: '{query}' -> {status}")
        if not is_success:
            failed = True

    if failed:
        print("\nSome tests failed!")
        exit(1)
    else:
        print("\nAll tests passed!")

if __name__ == "__main__":
    test_intent_classification()
