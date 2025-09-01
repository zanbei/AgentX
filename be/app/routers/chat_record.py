from fastapi import APIRouter, Request
from typing import List

from ..agent.agent import ChatRecord, ChatResponse, ChatRecordService

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}}
)

chat_service = ChatRecordService()


# List top 100 Chat Records
@router.get("/list_record")
def  list_chats() -> List[ChatRecord]:
    return chat_service.get_chat_records()

@router.get("/get_chat")
def get_chat(chat_id: str) -> ChatRecord | None:
    return chat_service.get_chat_record(chat_id)

@router.get("/list_chat_responses")
def list_chat_responses(chat_id: str) -> List[ChatResponse]:
    return chat_service.get_all_chat_responses(chat_id)

# delete chat record
@router.delete("/del_chat")
def del_chat(chat_id: str):
    chat_service.del_chat(chat_id)

@router.get("/get_file_content")
def get_file_content(chat_id: str) -> str:
    """
    Get file content from ChatResponse using chat_id.
    The content is stored in the first response (resp_no=0).
    """
    responses = chat_service.get_all_chat_responses(chat_id)
    if not responses:
        return ""
    
    # Get the first response which contains the S3 path
    first_response = next((r for r in responses if r.resp_no == 0), None)
    if not first_response:
        return ""
    
    return first_response.content
