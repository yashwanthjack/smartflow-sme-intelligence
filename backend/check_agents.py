import langchain.agents
print(f"LangChain Agents attributes: {dir(langchain.agents)}")

try:
    from langchain.agents import AgentExecutor
    print("AgentExecutor found in agents")
except:
    print("AgentExecutor NOT in agents")

try:
    from langchain.agents.agent import AgentExecutor
    print("AgentExecutor found in agents.agent")
except:
    print("AgentExecutor NOT in agents.agent")

try:
    from langchain.agents import create_react_agent
    print("create_react_agent found in agents")
except:
    print("create_react_agent NOT in agents")

try:
    from langchain.agents import initialize_agent
    print("initialize_agent found in agents")
except:
    print("initialize_agent NOT in agents")
