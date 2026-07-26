from langchain.tools import tool
from typing import Dict, Any, List
from pydantic import BaseModel, Field

# We use the existing Supervisor/Orchestrator's LLM
from app.agents.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

class SwarmTeamRequest(BaseModel):
    agents: List[str] = Field(description="List of agent roles to include in the team (e.g. ['TaxAgent', 'ForecastingAgent'])")
    task_description: str = Field(description="The financial task for this swarm team to resolve collaboratively.")
    entity_id: str = Field(description="The entity ID")

@tool("TeamCreateTool_SmartFlow")
async def create_swarm_team(request: SwarmTeamRequest) -> str:
    """AUTONOMOUS ACTION: Spin up a dynamic sub-team of specialist AI agents to handle a complex multi-disciplinary task."""
    
    # In a full swarm model, we would initialize each requested agent, pass them the context,
    # and use an internal router/bus to let them talk to each other.
    
    agents_str = ", ".join(request.agents)
    
    # For now, we simulate the 'swarm' execution by having a high-context LLM act as the combined unit.
    llm = get_llm()
    
    system_prompt = f"You are a collaborative task force comprising the following roles: {agents_str}.\n" \
                    f"You must resolve the following task for entity_id: {request.entity_id}\n" \
                    f"Please combine the perspectives of all roles to synthesize a comprehensive answer.\n"
                    
    # Note: In a complete implementation, we'd loop through each agent subclass 
    # (like CreditAdvisoryAgent, etc.) and let them execute their specific LangGraph node.
    # We will simulate the multi-agent response by letting the LLM act out the Swarm.
    
    response = await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=request.task_description)
    ])
    
    output = response.content if hasattr(response, 'content') else str(response)
    
    return f"🚀 **Swarm Team [{agents_str}] Output:**\n\n{output}"

class DirectAgentRequest(BaseModel):
    role: str = Field(description="The role/name of the agent to spawn (e.g., 'ForecastingAgent')")
    task: str = Field(description="The task for the agent.")

@tool("AgentTool_SmartFlow")
async def spin_up_agent(request: DirectAgentRequest) -> str:
    """Spawns an ephemeral SmartFlow agent for a specific task."""
    
    llm = get_llm()
    system_prompt = f"You are an expert SmartFlow Agent specialized as a {request.role}.\n" \
                    f"Perform your task concisely."
                    
    response = await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=request.task)
    ])
    
    return f"[{request.role} Report]:\n{response.content if hasattr(response, 'content') else str(response)}"
