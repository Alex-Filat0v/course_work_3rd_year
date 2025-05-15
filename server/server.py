from fastapi import FastAPI
from routes.auth_routes import auth_router
#from routes.user_routes import user_router
from routes.websocket_routes import ws_router
import uvicorn


app = FastAPI()

app.include_router(auth_router)
#app.include_router(user_router)
app.include_router(ws_router)


if __name__ == '__main__':
    uvicorn.run('server:app', reload=True)
