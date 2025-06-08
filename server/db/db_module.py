import asyncpg
from datetime import datetime
from hashlib import sha256
import os


class DataBaseConnector:
    def __init__(self):
        self.connection = None
        self.pool = None

    async def connect(self):
        # Для asyncpg нужно асинхронное подключение
        self.pool = await asyncpg.create_pool(
            user='postgres',  # Укажите ваши данные
            password='1234',
            database='CourseWork3',  # Имя базы данных для PostgreSQL
            host="localhost",
            port="5432"
        )
        await self.create_all_tables()

    async def disconnect(self):
        if self.connection and not self.connection.is_closed():
            await self.connection.close()
            print("🔌 Соединение с БД закрыто.")

    async def create_all_tables(self) -> None:
        async with self.pool.acquire() as connection:
            await connection.execute("""CREATE TABLE IF NOT EXISTS users (
                     surname varchar (35),
                     first_name varchar (35),
                     patronymic varchar (35),
                     mail varchar (80),
                     phone_number varchar(20),
                     birth_date DATE,
                     username varchar (40),
                     password varchar (100)
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
            print("good")
            exists = await connection.fetchrow(
                'SELECT * FROM users WHERE username = $1',
                user_data["username"]
            )

        if not exists:
            try:
                async with self.pool.acquire() as connection:
                    await connection.execute('''
                            INSERT INTO users(surname, first_name, patronymic, mail, phone_number, 
                            birth_date, username, password) VALUES($1, $2, $3, $4, $5, $6, $7, $8)''',
                                             user_data["surname"],
                                             user_data["first_name"],
                                             user_data["patronymic"],
                                             user_data["mail"],
                                             user_data["phone_number"],
                                             user_data["birth_date"],
                                             user_data["username"],
                                             user_data["password"]
                                             )
                return True
            except Exception as e:
                return e.__str__()
        else:
            return "This user name is already taken"

    async def drop_table(self):
        async with self.pool.acquire() as connection:
            await connection.execute("""DROP TABLE users""")


# Создаем единственный экземпляр здесь, в этом модуле.
db_connector = DataBaseConnector()


# Создаем функцию-зависимость, которую будут использовать роуты.
async def get_db() -> DataBaseConnector:
    return db_connector



async def main():
    db = DataBaseConnector()
    await db.connect()
    # await db.drop_table()
    date = datetime.strptime("2003-04-16", "%Y-%m-%d").date()

    # Пример регистрации пользователя
    registration_result = await db.user_registration({
        "surname": "Иванов",
        "first_name": "Иван",
        "patronymic": "Иванович",
        "mail": "ivan@example.com",
        "phone_number": "+79991234567",
        "birth_date": date,
        "username": "ivan",
        "password": "securepassword123"
    })
    print(registration_result)

    # Пример авторизации
    auth_result = await db.user_authorization({
        "username": "ivan",
        "password": "securepassword123"
    })
    print("Авторизация успешна:", auth_result)


if __name__ == '__main__':
    # Запуск асинхронного кода
    import asyncio

    asyncio.run(main())
