"""
Unit tests for SmartFlow intent classification (Supervisor Agent).
Tests the regex-based NLP intent classifier that routes user queries
to the correct financial agents.
"""
import pytest
from app.agents.supervisor_agent import classify_intent


class TestGeneralIntents:
    """Test that conversational queries are correctly classified as general."""

    @pytest.mark.parametrize("query,expected_subtype", [
        ("Hello!", "greeting"),
        ("hi there", "greeting"),
        ("good morning", "greeting"),
        ("namaste", "greeting"),
        ("who are you?", "identity"),
        ("what can you do", "identity"),
        ("thank you so much", "thanks"),
        ("bye", "farewell"),
        ("help me use this", "help"),
        ("what time is it?", "time"),
    ])
    def test_general_queries(self, query, expected_subtype):
        result = classify_intent(query)
        assert result["type"] == "general", f"Expected 'general' for '{query}', got {result}"
        assert result["subtype"] == expected_subtype


class TestSingleAgentRouting:
    """Test that domain-specific queries route to the correct single agent."""

    @pytest.mark.parametrize("query,expected_agent", [
        ("Show me overdue receivables and collection status", "collections"),
        ("What is my DSO and aging report?", "collections"),
        ("Check vendor payable status and schedule payment", "payments"),
        ("What are my DPO metrics and vendor payments?", "payments"),
        ("Check GSTR-1 and GSTR-3B filing status and ITC", "gst"),
        ("What is my input tax credit reconciliation?", "gst"),
        ("What is my credit score and loan eligibility?", "credit"),
        ("Show me cash runway and burn rate", "credit"),
    ])
    def test_single_agent_routing(self, query, expected_agent):
        result = classify_intent(query)
        assert result["type"] == "single", f"Expected 'single' for '{query}', got {result}"
        assert result["agent"] == expected_agent


class TestMultiAgentRouting:
    """Test that complex queries trigger multi-agent collaboration."""

    @pytest.mark.parametrize("query,expected_subtype", [
        ("Who should I pay first?", "payment_priority"),
        ("whom should I pay?", "payment_priority"),
        ("Should I take a loan?", "loan_advisory"),
        ("Can I borrow money for expansion?", "loan_advisory"),
        ("How is my business doing overall?", "core_health"),
        ("Am I safe to pay all vendors?", "affordability"),
        ("Should I collect or pay? What should I focus on?", "priority_decision"),
        ("Am I compliant? Any risks?", "risk_check"),
        ("Can I hire two developers?", "strategic_decision"),
    ])
    def test_multi_agent_queries(self, query, expected_subtype):
        result = classify_intent(query)
        assert result["type"] == "multi", f"Expected 'multi' for '{query}', got {result}"
        assert result["subtype"] == expected_subtype


class TestDirectToolQueries:
    """Test queries that should route to direct tool calls."""

    def test_highest_transaction(self):
        result = classify_intent("What is the highest transaction?")
        assert result["type"] == "multi"
        assert result["subtype"] == "highest_transaction"

    def test_highest_received(self):
        result = classify_intent("from whom did I got the highest payment?")
        assert result["type"] == "multi"
        assert result["subtype"] == "highest_received"


class TestEdgeCases:
    """Test edge cases and ambiguous queries."""

    def test_empty_query_falls_to_default(self):
        result = classify_intent("")
        # Empty query should default to multi-agent core_health
        assert result["type"] == "multi"

    def test_gibberish_falls_to_default(self):
        result = classify_intent("asdfghjkl qwerty")
        assert result["type"] == "multi"
        assert result["subtype"] == "core_health"

    def test_case_insensitivity(self):
        result1 = classify_intent("SHOW ME OVERDUE RECEIVABLES AND COLLECTION")
        result2 = classify_intent("show me overdue receivables and collection")
        assert result1 == result2
