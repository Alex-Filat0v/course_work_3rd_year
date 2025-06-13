from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from server.database.db_module import mongo_connector
from server.models import ChatOut
from server.models import MessageOut


chat_router = APIRouter()


class CreateGroupChatRequest(BaseModel):
    title: str
    participants: List[str]
    creator: str


def convert_chat_id(chat: dict) -> dict:
    if chat and '_id' in chat:
        chat['_id'] = str(chat['_id'])
    return chat


@chat_router.get("/chats/{username}", response_model=List[ChatOut])
async def get_chats(username: str):
    chats_from_db = await mongo_connector.get_user_chats(username)
    return [convert_chat_id(chat) for chat in chats_from_db]


@chat_router.post("/chats/group", response_model=ChatOut)
async def create_group_chat(request: CreateGroupChatRequest):
    if request.creator not in request.participants:
        request.participants.append(request.creator)

    chat_data = {
        "title": request.title,
        "is_group_chat": True,
        "participants": request.participants,
        "last_message": None
    }
    new_chat_from_db = await mongo_connector.create_chat(chat_data)
    if not new_chat_from_db:
        raise HTTPException(status_code=500, detail="Could not create group chat")

    return ChatOut.model_validate(convert_chat_id(new_chat_from_db))


@chat_router.post("/chats/direct/{user1}/{user2}", response_model=ChatOut)
async def create_direct_chat(user1: str, user2: str):
    participants = sorted([user1, user2])
    chat_data = {
        "is_group_chat": False,
        "participants": participants,
        "last_message": None
    }
    chat_from_db = await mongo_connector.create_chat(chat_data)
    if not chat_from_db:
        raise HTTPException(status_code=500, detail="Could not create direct chat")

    return ChatOut.model_validate(convert_chat_id(chat_from_db))


@chat_router.get("/chats/history/{chat_id}", response_model=List[MessageOut])
async def get_chat_history(chat_id: str):
    history_from_db = await mongo_connector.get_chat_history(chat_id)
    response = []
    for msg in history_from_db:
        msg['_id'] = str(msg['_id'])
        msg['chat_id'] = str(msg['chat_id'])
        response.append(MessageOut.model_validate(msg))
    return response
