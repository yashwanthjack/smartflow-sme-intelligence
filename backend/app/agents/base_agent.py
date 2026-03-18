# Base Agent class for SmartFlow agents
# Upgraded to use LangChain Tool-Calling (ReAct) pattern
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class BaseAgent(ABC):
    """Abstract base class for all SmartFlow agents.
    
    Supports two execution modes:
    1. Autonomous Tool-Calling (ReAct) — LLM decides which tools to call
    2. Fallback Static — For weak local models that can't do tool calling
    """
    
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        self.actions: List[Dict[str, Any]] = []
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Agent name for logging and identification."""
        pass
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt defining the agent's role and behavior."""
        pass
    
    @property
    @abstractmethod
    def tools(self) -> list:
        """List of tools available to this agent."""
        pass
    
    @abstractmethod
    async def run(self, task: str) -> Dict[str, Any]:
        """Execute the agent with a specific task."""
        pass

    async def run_mock(self, task: str) -> Dict[str, Any]:
        """
        Deterministic, zero-LLM execution path.

        This is designed for low-cost/dev environments where calling real LLMs
        is undesirable. Subclasses can override for richer behavior.
        """
        from app.db.database import SessionLocal
        from app.agents.tools import set_db_session

        db = SessionLocal()
        set_db_session(db)
        try:
            # Default behavior: call each tool once (when possible) and return outputs.
            # Tools are LangChain-wrapped callables; they expose `.invoke()` for direct calls.
            outputs: List[str] = []
            for t in (self.tools or []):
                try:
                    name = getattr(t, "name", None) or getattr(t, "__name__", "tool")
                    if name in {"get_overdue_invoices", "get_pending_payables", "get_cash_forecast", "check_gst_compliance", "get_entity_credit_score", "calculate_cash_runway"}:
                        result = t.invoke({"entity_id": self.entity_id})
                        outputs.append(str(result))
                except Exception as e:
                    outputs.append(f"{name} error: {e}")

            if not outputs:
                outputs = [f"{self.name} (mock mode) is enabled. No tool outputs available for this agent."]

            combined = "\n\n".join(outputs)
            self.log_action("agent_executed", {"mode": "mock", "output": combined[:500]})
            return {"output": combined, "agent": self.name}
        finally:
            db.close()
    
    async def run_with_tools(self, task: str) -> Dict[str, Any]:
        """Execute the agent using LangChain tool-calling AgentExecutor.
        
        The LLM autonomously decides which tools to call, reads outputs,
        and generates a final synthesized answer.
        """
        from app.agents.tools import set_db_session
        from app.db.database import SessionLocal
        from app.agents.llm import get_llm
        from app.config import settings
        
        db = SessionLocal()
        set_db_session(db)
        
        try:
            # If mock mode is enabled, never call an external LLM.
            if getattr(settings, "AI_MODE", "mock").lower() == "mock":
                return await self.run_mock(task)

            llm = get_llm()
            
            # Build the ReAct agent with tool calling
            agent_tools = self.tools
            
            # Bind tools to the LLM
            llm_with_tools = llm.bind_tools(agent_tools)
            
            # Use LangGraph's create_react_agent for LangChain 1.2+
            # Use LangGraph's create_react_agent for LangChain 1.2+
            from langgraph.prebuilt import create_react_agent
            
            agent_executor = create_react_agent(
                llm,
                agent_tools,
                prompt=self.system_prompt + "\n\nYou have access to tools. Use them to gather real data before answering. The entity_id for this business is: {entity_id}. Always use the entity_id when calling tools that require it."
            )
            
            # Run
            print(f"🤖 {self.name} executing with langgraph agent...")
            result = await agent_executor.ainvoke({
                "messages": [("human", task)],
                "entity_id": self.entity_id
            })
            
            # Extract final response from messages
            messages = result.get("messages", [])
            output = messages[-1].content if messages else str(result)
            
            # Log the tools that were used
            steps = result.get("intermediate_steps", [])
            tools_used = [step[0].tool for step in steps] if steps else []
            
            self.log_action("agent_executed", {
                "mode": "tool_calling",
                "tools_used": tools_used,
                "output": output[:500]
            })
            
            return {"output": output, "agent": self.name}
            
        except Exception as e:
            print(f"⚠️ {self.name} tool-calling failed: {e}")
            return {"output": f"Agent Error: {str(e)}", "agent": self.name}
        finally:
            db.close()
    
    def log_action(self, action_type: str, details: Dict[str, Any]):
        """Log an action taken by the agent."""
        self.actions.append({
            "agent": self.name,
            "entity_id": self.entity_id,
            "action_type": action_type,
            "details": details
        })
        self.persist_audit_log(action_type, details)

    def persist_audit_log(self, action_type: str, details: Dict[str, Any]):
        """Write audit log to database."""
        try:
            from app.db.database import SessionLocal
            from app.models.audit_log import AuditLog
            import json
            
            db = SessionLocal()
            try:
                # Determine severity based on action
                severity = "INFO"
                if "error" in str(details).lower():
                    severity = "ERROR"
                elif "urgent" in str(details).lower() or "critical" in str(details).lower():
                    severity = "WARNING"
                
                log = AuditLog(
                    agent_name=self.name,
                    event_type="AI_AGENT",
                    action=action_type,
                    severity=severity,
                    entity_id=self.entity_id,
                    details=json.dumps(details, default=str),
                    reasoning=details.get("output", "")[:500] if isinstance(details, dict) else str(details)[:500]
                )
                db.add(log)
                db.commit()
            except Exception as e:
                print(f"Failed to persist audit log: {e}")
            finally:
                db.close()
        except ImportError:
            pass  # functional even if DB not available
