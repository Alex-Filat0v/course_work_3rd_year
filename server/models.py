from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class MessageInDB(BaseModel):
    id: ObjectId = Field(alias="_id")
    chat_id: ObjectId
    author_username: str
    text: str
    created_at: datetime
    read_by: List[str] = []

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class MessageOut(BaseModel):
    id: str = Field(alias="_id")
    chat_id: str
    author_username: str
    text: str
    created_at: datetime

    class Config:
        populate_by_name = True
        @classmethod
        def model_validate(cls, obj, *args, **kwargs):
            if isinstance(obj, dict):
                if '_id' in obj:
                    obj['_id'] = str(obj['_id'])
                if 'chat_id' in obj:
                    obj['chat_id'] = str(obj['chat_id'])
            return super().model_validate(obj, *args, **kwargs)


class ChatOut(BaseModel):
    id: str = Field(alias="_id")
    title: Optional[str] = None
    is_group_chat: bool
    participants: List[str]
    last_message: Optional[dict] = None

    class Config:
        populate_by_name = True
        @classmethod
        def model_validate(cls, obj, *args, **kwargs):
            if isinstance(obj, dict) and '_id' in obj:
                obj['_id'] = str(obj['_id'])
            return super().model_validate(obj, *args, **kwargs)
