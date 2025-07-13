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