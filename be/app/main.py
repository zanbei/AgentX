from fastapi import FastAPI, HTTPException
from .routers import agent

app = FastAPI()
app.include_router(agent.router)