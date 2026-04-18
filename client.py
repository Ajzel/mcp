import os
import sys
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from pydantic import BaseModel

load_dotenv()


class AskRequest(BaseModel):
    message: str


def _extract_text(agent_response: dict) -> str:
    messages = agent_response.get("messages", [])
    if messages:
        return getattr(messages[-1], "content", str(messages[-1]))
    return str(agent_response)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent = None
    app.state.math_server = Path(__file__).resolve().parent / "mathserver.py"
    yield


async def get_agent(app: FastAPI):
    if app.state.agent is not None:
        return app.state.agent

    try:
        # Test with math only first - weather added back once math works
        client = MultiServerMCPClient(
            {
                "math": {
                    "command": sys.executable,
                    "args": [str(app.state.math_server)],
                    "transport": "stdio",
                },
            }
        )
        tools = await client.get_tools()
        print(f"Tools loaded: {[t.name for t in tools]}")
        model = ChatGroq(model=os.getenv("GROQ_MODEL", "qwen/qwen3-32b"))
        app.state.agent = create_react_agent(model, tools)
        return app.state.agent
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent init failed: {exc}")


app = FastAPI(title="MCP LangChain Agent API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/ask")
async def ask(request: AskRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message must not be empty")

    agent = await get_agent(app)
    agent_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": request.message}]}
    )
    return {"answer": _extract_text(agent_response)}