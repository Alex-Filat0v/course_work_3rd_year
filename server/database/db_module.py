import asyncpg
import motor.motor_asyncio
from bson import ObjectId
from typing import List


class DataBaseConnector:
    def __init__(self):
        self.connection = None
        self.pool = None

    async def connect(self) -> None:
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(
                    user='postgres',
                    password='1234',
                    database='CourseWork3',
                    host="localhost",
                    port="5432"
                )
                print("Соединение с PostgreSQL установлено.")
                await self.create_all_tables()
            except Exception as e:
                print(f"Ошибка подключения к PostgreSQL: {e}")

    async def disconnect(self) -> None:
        if self.pool:
            await self.pool.close()
            self.pool = None
            print("Соединение с PostgreSQL закрыто.")

    async def create_all_tables(self) -> None:
        async with self.pool.acquire() as connection:
            await connection.execute("""CREATE TABLE IF NOT EXISTS users (
                surname varchar (35),
                first_name varchar (35),
                patronymic varchar (35),
                mail varchar (80) UNIQUE,
                phone_number varchar(20) UNIQUE,
                birth_date DATE,
                username varchar (40) PRIMARY KEY,
                password varchar (100)
            );""")
            await connection.execute("""CREATE TABLE IF NOT EXISTS contacts (
                owner_username VARCHAR(40) REFERENCES users(username) ON DELETE CASCADE,
                contact_username VARCHAR(40) REFERENCES users(username) ON DELETE CASCADE,
                PRIMARY KEY (owner_username, contact_username)
            );""")

    async def user_authorization(self, user_data: dict) -> bool:
        async with self.pool.acquire() as connection:
            exists = await connection.fetchrow(
                'SELECT password FROM users WHERE username = $1',
                user_data["username"]
            )
            if exists:
                db_password = exists[0]
                return db_password == user_data["password"]
            return False

    async def user_registration(self, user_data: dict) -> str | bool:
        async with self.pool.acquire() as connection:

            exists = await connection.fetchrow(
                'SELECT username FROM users WHERE username = $1 OR mail = $2',
                user_data["username"], user_data["mail"]
            )

            if not exists:
                try:

                    await connection.execute('''
                        INSERT INTO users(surname, first_name, patronymic, mail, phone_number, birth_date, username, password) 
                        VALUES($1, $2, $3, $4, $5, $6, $7, $8)
                    ''',
                                             user_data["surname"], user_data["first_name"], user_data["patronymic"],
                                             user_data["mail"], user_data["phone_number"], user_data["birth_date"],
                                             user_data["username"], user_data["password"]
                                             )
                    return True
                except Exception as e:

                    print(f"Ошибка вставки в БД: {e}")
                    return f"Не удалось зарегистрировать пользователя. Возможно, данные не уникальны. ({e})"
            else:
                return "Это имя пользователя или email уже заняты"

    async def search_users(self, query: str, current_user: str, limit: int = 20) -> list:

        search_query = f"%{query}%"

        records = await self.pool.fetch(
            """SELECT username, first_name, surname FROM users 
               WHERE (username ILIKE $1 OR first_name ILIKE $1 OR surname ILIKE $1)
               AND username != $2
               LIMIT $3""",
            search_query, current_user, limit
        )

        return [dict(record) for record in records]

    async def get_contacts(self, owner_username: str) -> list:
        records = await self.pool.fetch(
            """SELECT u.username, u.first_name, u.surname 
               FROM contacts c
               JOIN users u ON c.contact_username = u.username
               WHERE c.owner_username = $1""",
            owner_username
        )

        return [dict(record) for record in records]

    async def add_contact(self, owner_username: str, contact_username: str) -> bool:
        try:
            await self.pool.execute(
                "INSERT INTO contacts (owner_username, contact_username) VALUES ($1, $2)",
                owner_username, contact_username
            )
            return True
        except asyncpg.exceptions.UniqueViolationError:
            return False


class MongoConnector:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self) -> None:
        if not self.client:
            self.client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
            self.db = self.client.messenger_db
            print("Соединение с MongoDB установлено.")

    async def disconnect(self) -> None:
        if self.client:
            self.client.close()
            print("Соединение с MongoDB закрыто.")

    async def save_message(self, message_data: dict) -> None:
        await self.db.messages.insert_one(message_data)

    async def get_chat_history(self, chat_id: str, limit: int = 50) -> list:
        try:

            chat_object_id = ObjectId(chat_id)

            cursor = self.db.messages.find(
                {"chat_id": chat_object_id}
            ).sort("created_at", -1).limit(limit)

            history = await cursor.to_list(length=limit)
            return history[::-1]
        except Exception as e:
            print(f"Ошибка при извлечении истории чата ({chat_id}): {e}")
            return []

    async def get_user_chats(self, username: str) -> list:
        cursor = self.db.chats.find({"participants": username})
        return await cursor.to_list(length=100)

    async def create_chat(self, chat_data: dict) -> list | dict:

        if not chat_data['is_group_chat']:
            existing_chat = await self.db.chats.find_one({
                "is_group_chat": False,
                "participants": {"$all": chat_data['participants'], "$size": 2}
            })
            if existing_chat:
                return existing_chat

        result = await self.db.chats.insert_one(chat_data)
        new_chat = await self.db.chats.find_one({"_id": result.inserted_id})
        return new_chat

    async def update_last_message(self, chat_id: str, message: dict) -> None:
        await self.db.chats.update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": {"last_message": message}}
        )


db_connector = DataBaseConnector()
mongo_connector = MongoConnector()
