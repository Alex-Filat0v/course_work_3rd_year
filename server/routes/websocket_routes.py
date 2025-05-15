from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

ws_router = APIRouter()

connected_clients: List[WebSocket] = []


@ws_router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str) -> None:
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for client in connected_clients:
                if client != websocket:
                    await client.send_text(f"{username}: {data}")
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
