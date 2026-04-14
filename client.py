from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from dotenv import load_dotenv
load_dotenv()

import asyncio
import sys
from pathlib import Path

async def main():
    project_root = Path(__file__).resolve().parent
    math_server = project_root / "mathserver.py"
    client = MultiServerMCPClient(
        {
            "math":{
                "command": sys.executable,
                "args": [str(math_server)],
                "transport":"stdio",

            },
            "weather": {
                "url":"http://localhost:8000/mcp",
                "transport":"streamable-http",
            }
            
        }
    ) 
    
    import os
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

    tools = await client.get_tools()
    # qwen-qwq-32b was decommissioned; see https://console.groq.com/docs/deprecations
    model = ChatGroq(model=os.getenv("GROQ_MODEL", "qwen/qwen3-32b"))
    agent=create_react_agent(
        model, tools
    )
    
    math_response = await agent.ainvoke(
        {"messages":[{"role":"user","content":"What is (3+5)*12?"}]}
    )
    
    print("Math Response:", math_response['messages'][-1].content)
    
    weather_response = await agent.ainvoke(
        {"messages":[{"role":"user","content":"What is the weather in Bangalore?"}]}
    )
    print("Weather Response:", weather_response['messages'][-1].content)    
    
asyncio.run(main())