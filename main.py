from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from server.routes.auth_routes import auth_router
from server.routes.chat_routes import chat_router
from server.routes.websocket_routes import ws_router
from server.routes.user_routes import user_router
from server.database.db_module import db_connector, mongo_connector


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Приложение запускается...")
    await db_connector.connect()
    await mongo_connector.connect()
    yield

    print("Приложение останавливается...")
    await db_connector.disconnect()
    await mongo_connector.disconnect()

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(ws_router)
app.include_router(user_router)

if __name__ == '__main__':
    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True)
