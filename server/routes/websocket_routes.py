import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
from datetime import datetime
from bson import ObjectId
from server.database.db_module import mongo_connector


ws_router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: str):
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []
        self.active_connections[chat_id].append(websocket)
        print(f"Подключился клиент к чату {chat_id}. Всего в чате: {len(self.active_connections[chat_id])}")

    def disconnect(self, websocket: WebSocket, chat_id: str):
        if chat_id in self.active_connections:
            self.active_connections[chat_id].remove(websocket)
            print(f"Отключился клиент от чата {chat_id}. Осталось в чате: {len(self.active_connections[chat_id])}")

    async def broadcast(self, message: str, chat_id: str):
        if chat_id in self.active_connections:
            for connection in self.active_connections[chat_id]:
                await connection.send_text(message)


manager = ConnectionManager()


@ws_router.websocket("/ws/{chat_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str, username: str):
    await manager.connect(websocket, chat_id)
    try:
        while True:
            data_json = await websocket.receive_text()
            data = json.loads(data_json)

            message_type = data.get("type")

            if message_type == "text_message":
                text = data.get("text")
                created_time = datetime.now()

                message_to_save = {
                    "chat_id": ObjectId(chat_id),
                    "author_username": username,
                    "text": text,
                    "created_at": created_time,
                }

                result = await mongo_connector.db.messages.insert_one(message_to_save)

                message_to_broadcast = {
                    "type": "new_message",
                    "_id": str(result.inserted_id),
                    "chat_id": chat_id,
                    "author_username": username,
                    "text": text,
                    "created_at": created_time.isoformat(),
                }

                await manager.broadcast(json.dumps(message_to_broadcast), chat_id)
                await mongo_connector.update_last_message(chat_id, message_to_broadcast)

            elif message_type == "read_receipt":
                message_ids = data.get("message_ids", [])
                update_to_broadcast = {
                    "type": "messages_read",
                    "chat_id": chat_id,
                    "message_ids": message_ids,
                    "read_by_user": username
                }
                await manager.broadcast(json.dumps(update_to_broadcast), chat_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_id)
    except Exception as e:
        print(f"Произошла ошибка в WebSocket: {e}")
        manager.disconnect(websocket, chat_id)
