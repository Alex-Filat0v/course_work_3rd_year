import httpx
import asyncio
import websockets
import sys
from hashlib import sha256


async def receive_messages(ws) -> None:
    while True:
        msg = await ws.recv()
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()
        print(f"{msg}")
        print("Введите сообщение: ", end="", flush=True)


async def send_messages(ws) -> None:
    while True:
        msg = await asyncio.get_event_loop().run_in_executor(None, input, "Введите сообщение: ")
        await ws.send(msg)


async def main() -> None:
    async with httpx.AsyncClient() as client:
        username = str(input('Введите логин(ir):'))
        password = str(input('Введите пароль(1234):'))
        password = sha256(password.encode('utf-8')).hexdigest()
        auth = {
            "username": username,
            "password": password
        }
        resp = await client.post("http://127.0.0.1:8000/auth", json=auth)
        if resp.status_code != 200:
            print("Неверный логин или пароль")
            await main()

    print("Авторизация успешна, подключение к вебсокету...")

    async with websockets.connect(f"ws://127.0.0.1:8000/ws/{auth['username']}") as ws:
        receive_task = asyncio.create_task(receive_messages(ws))
        send_task = asyncio.create_task(send_messages(ws))
        await asyncio.gather(receive_task, send_task)


if __name__ == '__main__':
    asyncio.run(main())
