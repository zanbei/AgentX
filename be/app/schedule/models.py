from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ScheduleCreate(BaseModel):
    """Model for creating a new schedule."""
    agentId: str
    cronExpression: str

class Schedule(BaseModel):
    """Model representing a schedule."""
    id: str
    agentId: str
    agentName: str
    cronExpression: str
    status: str
    createdAt: str
    updatedAt: str
