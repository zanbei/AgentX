from datetime import datetime
import uuid
import json
import os
import boto3
from fastapi import APIRouter, Request, BackgroundTasks, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Dict, Tuple, Optional, AsyncGenerator
from ..agent.agent import AgentPO, AgentType, ModelProvider, AgentTool, AgentPOService, ChatRecord, ChatResponse, ChatRecordService
from ..agent.event_serializer import EventSerializer
from ..utils.aws_config import get_aws_region

agent_service = AgentPOService()
chat_reccord_service = ChatRecordService()

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
    responses={404: {"description": "Not found"}}
)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, str]:
    """
    Upload a file to S3, create a chat record, and return both S3 path and chat ID.
    """
    print(f"Uploading file: {file.filename}, Content-Type: {file.content_type}")
    try:
        # Initialize S3 client
        s3 = boto3.client('s3', region_name=get_aws_region())
        bucket_name = 'a-web-uw2' # Replace with your actual bucket name
        print(f"S3 client initialized for bucket: {bucket_name}")
        s3_key = f'agentx/{file.filename}'
        
        # Read file content
        content = await file.read()
        content_size = len(content)
        print(f"Read file content, size: {content_size} bytes")
        
        # Create a file-like object from the content
        from io import BytesIO
        file_obj = BytesIO(content)
        file_obj.seek(0)  # Ensure file pointer is at the beginning
        
        # Upload file to S3
        print(f"Uploading to S3: bucket={bucket_name}, key={s3_key}")
        s3.upload_fileobj(
            file_obj,
            bucket_name,
            s3_key,
            ExtraArgs={'ContentType': file.content_type}
        )
        print("S3 upload completed successfully")
        
        # Generate chat ID
        chat_id = uuid.uuid4().hex
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s3_path = f's3://{bucket_name}/{s3_key}'
        
        # Save file locally
        file_ext = os.path.splitext(file.filename)[1]
        local_file_path = f"/Users/anbei/Desktop/AgentX/be/uploads/{chat_id}{file_ext}"
        # Ensure the uploads directory exists
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        # Create a new BytesIO object for local file save
        local_file_obj = BytesIO(content)
        with open(local_file_path, "wb") as f:
            f.write(local_file_obj.read())
        print(f"File saved locally at: {local_file_path}")
        
        chat_record = ChatRecord(
            id=chat_id,
            agent_id="file_upload",  # Special agent ID for file uploads
            user_message=f"File uploaded: {local_file_path}",
            create_time=current_time
        )
        chat_reccord_service.add_chat_record(chat_record)
        
        # Create chat response with both paths
        chat_resp = ChatResponse(
            chat_id=chat_id,
            resp_no=0,
            content=local_file_path,  # Store local path for agent to use
            create_time=current_time
        )
        chat_reccord_service.add_chat_response(chat_resp)
        
        return {
            "s3_path": s3_path,
            "file_path": local_file_path,
            "chat_id": chat_id
        }
        
    except Exception as e:
        raise Exception(f"Failed to upload file to S3: {str(e)}")

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

@router.post("/createOrUpdate")
async def create_agent(request: Request) -> AgentPO:
    """
    Create a new agent.
    :param agent: The agent data to create.
    :return: Confirmation of agent creation.
    """
    
    agent = await request.json()
    agent_id = uuid.uuid4().hex
    if agent and agent.get("id"):
        agent_service.delete_agent(agent["id"])
        agent_id = agent["id"]

    tools = []
    if agent.get("tools"):
        tools = [t for tool in agent["tools"] if (t:= AgentTool.model_validate(tool)) is not None]

    agent_po = AgentPO(
        id= agent_id,
        name=agent.get("name"),
        display_name=agent.get("display_name"),
        description=agent.get("description"),
        agent_type=AgentType(agent.get("agent_type")),
        model_provider=ModelProvider(agent.get("model_provider")),
        model_id=agent.get("model_id"),
        sys_prompt=agent.get("sys_prompt"),
        tools= tools,
        envs=agent.get("envs", ""),
        extras=agent.get("extras"),
    )
    agent_service.add_agent(agent_po)
    return agent_po

async def parse_chat_request_and_add_record(request: Request) -> Tuple[Optional[str], Optional[str], str, bool]:
    """
    Parse a chat request to extract agent_id, user_message, and create a chat record.
    
    :param request: The request containing the chat parameters.
    :return: A tuple of (agent_id, user_message, chat_id, chat_record_enabled).
    """
    data = await request.json()
    agent_id = data.get("agent_id")
    user_message = data.get("user_message")
    chat_record_enabled = data.get("chat_record_enabled", True)  # Default to True if not provided
    
    # Log the received message content
    print(f"Received chat request - Agent ID: {agent_id}")
    print(f"User message content: {user_message}")
    if user_message and "File Content:" in user_message:
        print("Message includes uploaded file content")
    
    # Create a chat record if chat_record_enabled is True
    chat_id = uuid.uuid4().hex
    if chat_record_enabled:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat_record = ChatRecord(id=chat_id, agent_id=agent_id, user_message=user_message, create_time=current_time)
        chat_reccord_service.add_chat_record(chat_record)
    
    return agent_id, user_message, chat_id, chat_record_enabled

async def process_chat_events(agent_id: str, user_message: str, chat_id: str, chat_record_enabled: bool = True) -> AsyncGenerator[Dict, None]:
    """
    Process chat events and save responses to the database if chat_record_enabled is True.
    
    :param agent_id: The ID of the agent to chat with.
    :param user_message: The user's message to process.
    :param chat_id: The ID of the chat record.
    :param chat_record_enabled: Whether to save chat responses to the database.
    :yield: Chat events.
    """
    resp_no = 0
    async for event in agent_service.stream_chat(agent_id, user_message):
        if chat_record_enabled and ("message" in event and "role" in event["message"]):
            chat_resp = ChatResponse(
                chat_id=chat_id, 
                resp_no=resp_no, 
                content=json.dumps(event), 
                create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            chat_reccord_service.add_chat_response(chat_resp)
            resp_no += 1
        yield event

@router.post("/stream_chat")
async def stream_chat(request: Request) -> StreamingResponse:
    """
    Stream chat messages from an agent.
    :param request: The request containing the chat parameters.
    :return: A stream of chat messages.
    """
    agent_id, user_message, chat_id, chat_record_enabled = await parse_chat_request_and_add_record(request)
    
    if not agent_id or not user_message:
        return "Agent ID and user message are required."
    
    async def event_generator():
        """
        Generator function to yield SSE formatted events.
        """
        async for event in process_chat_events(agent_id, user_message, chat_id, chat_record_enabled):
            # Format the event as an SSE
            yield EventSerializer.format_as_sse(event)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

@router.post("/async_chat")
async def async_chat(request: Request, background_tasks: BackgroundTasks) -> JSONResponse:
    """
    Process chat messages from an agent asynchronously.
    This endpoint returns immediately with a chat ID and processes the request in the background.
    
    :param request: The request containing the chat parameters.
    :param background_tasks: FastAPI's BackgroundTasks for background processing.
    :return: A JSON response with the chat ID.
    """
    agent_id, user_message, chat_id, chat_record_enabled = await parse_chat_request_and_add_record(request)
    
    if not agent_id or not user_message:
        return JSONResponse(
            status_code=400,
            content={"error": "Agent ID and user message are required."}
        )
    
    # Add the processing task to background tasks
    background_tasks.add_task(
        process_chat_in_background,
        agent_id=agent_id,
        user_message=user_message,
        chat_id=chat_id,
        chat_record_enabled=chat_record_enabled
    )
    
    # Return immediately with the chat ID
    return JSONResponse(
        content={
            "status": "processing",
            "chat_id": chat_id,
            "message": "Your request is being processed in the background."
        }
    )

async def process_chat_in_background(agent_id: str, user_message: str, chat_id: str, chat_record_enabled: bool = True):
    """
    Process a chat message in the background.
    
    :param agent_id: The ID of the agent to chat with.
    :param user_message: The user's message to process.
    :param chat_id: The ID of the chat record.
    :param chat_record_enabled: Whether to save chat responses to the database.
    """
    try:
        async for _ in process_chat_events(agent_id, user_message, chat_id, chat_record_enabled):
            pass  # We just need to consume the generator
        print(f"Background processing completed for chat {chat_id}")
    except Exception as e:
        # Log the error
        print(f"Error in background processing for chat {chat_id}: {str(e)}")

@router.get("/tool_list")
def available_agent_tools() -> List[AgentTool]:
    """
    List all available agent tools.
    :return: A list of available agent tools.
    """
    return agent_service.get_all_available_tools()
