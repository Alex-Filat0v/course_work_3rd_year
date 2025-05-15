import sqlite3
from hashlib import sha256
import os


class DataBaseConnector:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, 'database.db')

        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_all_tables()

    def create_all_tables(self) -> None:
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                 surname TEXT (35),
                 first_name TEXT (35),
                 patronymic TEXT (35),
                 mail TEXT (80),
                 phone_number varchar(20),
                 birth_date DATE,
                 username TEXT (40),
                 password TEXT (100)
                 );""")
        self.connection.commit()

    def user_authorization(self, user_data: dict) -> bool:
        self.cursor.execute('SELECT Password FROM users WHERE username = ?', (user_data["username"],))
        exists = self.cursor.fetchone()

        if exists:
            db_password = exists[0]

            return db_password == user_data["password"]

        return False

    def user_registration(self, user_data: dict) -> str | bool:
        self.cursor.execute('')

        #НАПИСАТЬ ЗАПРОС НА ПРОВЕРКУ НЕ ТОЛЬКО ЛОГИНА, НО И НОМЕРА ТЕЛЕФОНА, ПОЧТЫ И ЛОГИНА!!!!
        self.cursor.execute('SELECT 1 FROM users WHERE username = ?', (user_data["username"],))
        exists = self.cursor.fetchone()

        if not exists:
            try:
                self.cursor.execute('''
                                        INSERT INTO users (surname, first_name, patronymic, mail, phone_number, 
                                        birth_date, username, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                                    (
                                        user_data["surname"],
                                        user_data["first_name"],
                                        user_data["patronymic"],
                                        user_data["mail"],
                                        user_data["phone_number"],
                                        user_data["birth_date"],
                                        user_data["username"],
                                        user_data["password"]
                                    ))
                self.connection.commit()
                return True
            except Exception as e:
                return e.__str__()

        else:
            return "This user name is already taken"

    def drop_table(self):
        self.cursor.execute("""DROP TABLE threats""")
        self.connection.commit()
