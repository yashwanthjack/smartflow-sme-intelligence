"""
Unit tests for SmartFlow AI Agents.
Tests agent behavior with mocked LLM to avoid real API calls.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestSupervisorAgent:
    """Test the SupervisorAgent orchestration logic."""

    @pytest.mark.asyncio
    async def test_general_query_no_agent_invoked(self, patch_llm):
        """Greetings should be handled without invoking any financial agent."""
        from app.agents.supervisor_agent import SupervisorAgent

        supervisor = SupervisorAgent()

        with patch.object(supervisor, "_log_interaction"):
            result = await supervisor.run("test-entity", "Hello!")

        assert result["success"] is True
        assert result["agent_used"] == "SmartFlow Copilot"
        assert result["intent"] == "general"
        assert "SmartFlow" in result["output"] or "morning" in result["output"].lower() or "👋" in result["output"]

    @pytest.mark.asyncio
    async def test_single_agent_routing(self, patch_llm):
        """A domain-specific query should route to the correct single agent."""
        from app.agents.supervisor_agent import SupervisorAgent

        supervisor = SupervisorAgent()

        # Mock the agent runner
        mock_runner = AsyncMock(return_value={"output": "Collections report: 5 overdue invoices"})
        supervisor.agent_runners["collections"] = mock_runner

        with patch.object(supervisor, "_log_interaction"):
            result = await supervisor.run("test-entity", "Show overdue receivables and collection aging")

        assert result["success"] is True
        assert result["agent_used"] == "collections"
        mock_runner.assert_called_once()

    @pytest.mark.asyncio
    async def test_multi_agent_collaboration(self, patch_llm):
        """Complex queries should invoke multiple agents and synthesize."""
        from app.agents.supervisor_agent import SupervisorAgent

        supervisor = SupervisorAgent()

        # Mock both runners
        supervisor.agent_runners["payments"] = AsyncMock(
            return_value={"output": "Payments: ₹2L pending"}
        )
        supervisor.agent_runners["credit"] = AsyncMock(
            return_value={"output": "Credit score: 720"}
        )

        with patch.object(supervisor, "_log_interaction"):
            result = await supervisor.run("test-entity", "Who should I pay first?")

        assert result["success"] is True
        assert "payments" in result["agent_used"]

    @pytest.mark.asyncio
    async def test_agent_error_handling(self, patch_llm):
        """If an agent raises an exception, supervisor should handle gracefully."""
        from app.agents.supervisor_agent import SupervisorAgent

        supervisor = SupervisorAgent()

        # Make collections agent raise an error
        supervisor.agent_runners["collections"] = AsyncMock(side_effect=Exception("DB connection failed"))

        with patch.object(supervisor, "_log_interaction"):
            result = await supervisor.run("test-entity", "Show overdue receivables and collection aging")

        # Should still return a result (error fallback), not crash
        assert isinstance(result, dict)


class TestLLMConfiguration:
    """Test that LLM configuration loads correctly."""

    def test_get_llm_raises_without_api_key(self):
        """Should raise ValueError if GOOGLE_API_KEY is not set."""
        from app.agents import llm as llm_module

        # Temporarily clear the key
        original = llm_module.GOOGLE_API_KEY
        llm_module.GOOGLE_API_KEY = None
        try:
            with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
                llm_module.get_llm()
        finally:
            llm_module.GOOGLE_API_KEY = original

    def test_gemini_model_name_configured(self):
        """Verify the model name is set to Gemini."""
        from app.agents.llm import GEMINI_MODEL

        assert "gemini" in GEMINI_MODEL.lower()
