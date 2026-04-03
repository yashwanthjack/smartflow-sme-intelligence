import operator
from typing import Annotated, List, Literal, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, add_messages, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from app.agents.supervisor_agent import classify_intent

from app.agents.llm import get_llm
from app.agents.collections_agent import CollectionsAgent
from app.agents.payments_agent import PaymentsAgent
from app.agents.gst_agent import GSTAgent
from app.agents.credit_advisory_agent import CreditAdvisoryAgent
from app.agents.decision_advisor_agent import DecisionAdvisorAgent
from app.db.database import SessionLocal
from app.models.audit_log import AuditLog

def replace_value(old, new):
    return new

class AgentState(BaseModel):
    messages: Annotated[list, add_messages] = []
    entity_id: str
    active_agent: Annotated[Optional[str], replace_value] = None
    agent_reports: Annotated[list, operator.add] = []
    task_description: Annotated[Optional[str], replace_value] = None


# Handoff tool as used in ai-launchpad
@tool
def handoff_to_agent(
    agent_name: Literal["CollectionsAgent", "PaymentsAgent", "GSTAgent", "CreditAdvisoryAgent", "DecisionAdvisorAgent"],
    task_description: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    """Delegate a specific task to a specialized financial agent.
    
    Args:
        agent_name: The name of the agent to handoff the task to.
        task_description: Clear instructions on what data to fetch or analyze.
    """
    update = {
        "active_agent": agent_name,
        "task_description": task_description,
        "messages": [ToolMessage(
            name=f"handoff_to_{agent_name}",
            content=f"Delegated task to {agent_name}: {task_description}",
            tool_call_id=tool_call_id,
        )],
    }
    
    return Command(
        goto=f"call_{agent_name}",
        update=update
    )

# Worker node factory
def create_worker_node(agent_class, name):
    async def worker_node(state: AgentState, config: RunnableConfig):
        print(f"🤖 Worker {name} executing for entity {state.entity_id}...")
        
        # Initialize the actual agent class with database access
        agent = agent_class(state.entity_id)
        
        # Use the specific task description provided by the supervisor
        query = state.task_description or state.messages[0].content
        
        # Run the agent (which uses its own tools)
        report = await agent.run(query)
        
        # Log to audit table
        db = SessionLocal()
        try:
            log = AuditLog(
                entity_id=state.entity_id,
                agent_name=name,
                event_type="SYSTEM",
                action=f"Worker {name} processed task",
                severity="INFO",
                reasoning=str(report),
                trace_id=state.entity_id # Use entity_id as simple trace for now
            )
            db.add(log)
            db.commit()
        except Exception as e:
            print(f"Audit logging failed: {e}")
        finally:
            db.close()

        # Create a clean Human message for the supervisor to see the result
        ai_message = HumanMessage(
            content=f"--- {name} REPORT ---\n{report}\n\nPlease synthesize the above report and provide the final answer to the user.",
        )
        
        return {
            "messages": [ai_message],
            "agent_reports": [report]
        }
    return worker_node

# Supervisor node
async def supervisor_node(state: AgentState):
    llm = get_llm()
    # Bind the handoff tool
    tools = [handoff_to_agent]
    llm_with_tools = llm.bind_tools(tools)
    
    system_prompt = f"""You are the SmartFlow Executive Supervisor.
Current Date: {datetime.now().strftime("%Y-%m-%d")}
Entity ID: {state.entity_id}

Your goal is to answer the user's financial query by delegating tasks to specialists.
Workers:
- CollectionsAgent: Overdue invoices, payment reminders, customer aging.
- PaymentsAgent: Vendor payments, cash flow forecasts, pending bills, historical transactions (ledger).
- GSTAgent: Tax compliance, GSTR-1/3B filing status, ITC reconciliation.
- CreditAdvisoryAgent: Credit score, risk assessment, loan eligibility, cash runway.
- DecisionAdvisorAgent: Strategic business advice, burn rate analysis.

RULES:
1. Use 'handoff_to_agent' to get data from specialists.
2. If you have enough information, provide a final synthesized answer directly.
3. If the user asks for factual info, ask the PaymentsAgent.
4. DO NOT hallucinate. Use only data from agent reports.
5. If no agents are needed or task is complete, answer without calling tools.
6. CRITICAL FOR TOOLS: When calling a tool (like handoff), DO NOT output any conversational text or explanation whatsoever. Your response must consist ONLY of the tool call format. Do not say "I will now do X".
"""
    
    response = await llm_with_tools.ainvoke([
        SystemMessage(content=system_prompt)
    ] + state.messages)
    
    # Log supervisor action
    db = SessionLocal()
    try:
        log = AuditLog(
            entity_id=state.entity_id,
            agent_name="ExecutiveSupervisor",
            event_type="SYSTEM",
            action="Supervisor decision",
            severity="INFO",
            reasoning=response.content if hasattr(response, 'content') else str(response),
            trace_id=state.entity_id
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"Audit logging failed: {e}")
    finally:
        db.close()

    return {"messages": [response]}

# Router logic
def supervisor_router(state: AgentState):
    last_message = state.messages[-1]
    if last_message.tool_calls:
        return "handoff_tools"
    return END

# Graph construction
def create_langgraph_supervisor():
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("handoff_tools", ToolNode([handoff_to_agent]))
    
    # Add worker nodes
    workers = {
        "CollectionsAgent": CollectionsAgent,
        "PaymentsAgent": PaymentsAgent,
        "GSTAgent": GSTAgent,
        "CreditAdvisoryAgent": CreditAdvisoryAgent,
        "DecisionAdvisorAgent": DecisionAdvisorAgent
    }
    
    for name, cls in workers.items():
        node_name = f"call_{name}"
        builder.add_node(node_name, create_worker_node(cls, name))
        builder.add_edge(node_name, "supervisor") # Always back to supervisor
        
    # Set entry point
    builder.set_entry_point("supervisor")
    
    # Add edges
    builder.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "handoff_tools": "handoff_tools",
            END: END
        }
    )
    
    return builder.compile(checkpointer=MemorySaver())

# Global graph instance
_graph = create_langgraph_supervisor()

async def run_langgraph_supervisor(entity_id: str, query: str):
    """Entry point for the SmartFlow multi-agent system."""
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "entity_id": entity_id,
        "agent_reports": []
    }
    
    config = {"configurable": {"thread_id": entity_id}}
    
    # Pre-classify intent for the response model
    intent_dict = classify_intent(query)
    intent = intent_dict.get("subtype") or intent_dict.get("agent") or "unknown"
    
    final_state = await _graph.ainvoke(initial_state, config=config)
    
    # Extract the total output content correctly
    messages = final_state.get("messages", [])
    if not messages:
        return {
            "agent_used": "langgraph_supervisor",
            "intent": intent,
            "output": "I encountered an error analyzing your data. Please try again.",
            "success": False
        }
        
    last_msg = messages[-1]
    output = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
    
    return {
        "agent_used": "langgraph_supervisor",
        "intent": intent,
        "output": output,
        "success": True,
        "reports": final_state.get("agent_reports", [])
    }
