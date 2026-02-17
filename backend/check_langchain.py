try:
    from langchain.agents import AgentExecutor
    print("Found AgentExecutor in langchain.agents")
except ImportError as e:
    print(f"Error 1: {e}")

try:
    from langchain.agents.agent import AgentExecutor
    print("Found AgentExecutor in langchain.agents.agent")
except ImportError as e:
    print(f"Error 2: {e}")

try:
    from langchain.agents import create_react_agent
    print("Found create_react_agent in langchain.agents")
except ImportError as e:
    print(f"Error 3: {e}")
    
try:
    import langchain
    print(f"LangChain Version: {langchain.__version__}")
except:
    print("Could not get version")
