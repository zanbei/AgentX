from fastapi import FastAPI, HTTPException
import os

from .routers import agent
from .routers import mcp
from .routers import chat_record
from .routers import schedule

app = FastAPI()

# Read APP_ENV environment variable and set URL prefix accordingly
app_env = os.environ.get("APP_ENV", "")
url_prefix = "/api" if app_env == "production" else ""

app.include_router(agent.router, prefix=url_prefix)
app.include_router(mcp.router, prefix=url_prefix)
app.include_router(chat_record.router, prefix=url_prefix)
app.include_router(schedule.router, prefix=url_prefix)

@app.get("/")
def home():
    return {"App": "AgentX-BE"}
