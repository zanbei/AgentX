import uuid

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from typing import List
from ..agent.agent import AgentPO, AgentType, ModelProvider, Tools, AgentPOService

agent_service = AgentPOService()

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
    responses={404: {"description": "Not found"}}
)

@router.get("/list")
def list_agents() -> List[AgentPO]:
    """
    List all agents.
    :return: A list of agents.
    """
    return agent_service.list_agents()

@router.get("/get/{agent_id}")
def get_agent(agent_id: str) -> AgentPO:
    """
    Get a specific agent by ID.
    :param agent_id: The ID of the agent to retrieve.
    :return: Details of the specified agent.
    """
    return agent_service.get_agent(agent_id)

@router.delete("/delete/{agent_id}")
def delete_agent(agent_id: str) -> bool:
    """
    Delete a specific agent by ID.
    :param agent_id: The ID of the agent to delete.
    :return: True if deletion was successful, False otherwise.
    """
    return agent_service.delete_agent(agent_id)

@router.post("/create")
async def create_agent(request: Request) -> AgentPO:
    """
    Create a new agent.
    :param agent: The agent data to create.
    :return: Confirmation of agent creation.
    """
    agent = await request.json()
    print(agent)
    tools = []
    if agent.get("tools"):
        tools = [t for tool in agent["tools"] if (t:= Tools.getToolByName(tool))]

    agent_po = AgentPO(
        id= uuid.uuid4().hex,
        name=agent.get("name"),
        display_name=agent.get("display_name"),
        description=agent.get("description"),
        agent_type=AgentType[agent.get("agent_type")],
        model_provider=ModelProvider[agent.get("model_provider")],
        model_id=agent.get("model_id"),
        sys_prompt=agent.get("sys_prompt"),
        tools= tools,
    )
    agent_service.add_agent(agent_po)
    return agent_po

@router.post("/stream_chat")
async def stream_chat(request: Request) -> StreamingResponse:
    """
    Stream chat messages from an agent.
    :param request: The request containing the chat parameters.
    :return: A stream of chat messages.
    """
    data = await request.json()
    agent_id = data.get("agent_id")
    user_message = data.get("user_message")
    
    if not agent_id or not user_message:
        return "Agent ID and user message are required."
    
    return StreamingResponse(
        agent_service.stream_chat(agent_id, user_message),
        media_type="text/event-stream"
    ) 