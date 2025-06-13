import os
import json
import requests
from hashlib import sha256
from PyQt6 import QtWidgets, uic


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self, window_manager=None):
        super().__init__()
        self.window_manager = window_manager

        self.current_dir = os.path.dirname(__file__)
        self.session_file = os.path.join(self.current_dir, '..', 'session.json')

        file_dir = os.path.join(self.current_dir, "../templates/login.ui")
        uic.loadUi(file_dir, self)

        self.user_data = None
        self.toolButton_login.clicked.connect(self.login)

    def save_session(self, username, hashed_password):
        session_data = {
            "username": username,
            "password_hash": hashed_password
        }
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f)
        print("Сессия сохранена.")

    def clear_session(self):
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
            print("Сессия очищена.")

    def load_and_login(self):
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)

                self.lineEdit_login.setText(session_data.get("username", ""))

                self.perform_login(
                    session_data.get("username"),
                    session_data.get("password_hash"),
                    is_auto_login=True
                )
            except (json.JSONDecodeError, KeyError):
                self.clear_session()

    def login(self):
        username = self.lineEdit_login.text()
        password = self.lineEdit_password.text()

        if username and password:
            hashed_password = sha256(password.encode('utf-8')).hexdigest()
            self.perform_login(username, hashed_password)
        else:
            self.label_error.setText("*Обязательно заполните все поля для входа")

    def perform_login(self, username, password_or_hash, is_auto_login=False):
        auth_data = {
            "username": username,
            "password": password_or_hash,
        }

        try:
            response = requests.post(
                "http://127.0.0.1:8000/auth",
                json=auth_data,
                timeout=10
            )

            if response.status_code == 200:
                self.user_data = response.json()

                if not is_auto_login and self.checkBox.isChecked():
                    self.save_session(username, password_or_hash)
                elif not is_auto_login and not self.checkBox.isChecked():
                    self.clear_session()

                self.main()
            else:
                error_detail = response.json().get('detail', 'Неизвестная ошибка')
                self.label_error.setText(f"*{error_detail}")
                if is_auto_login:
                    self.clear_session()

        except requests.exceptions.RequestException as e:
            self.label_error.setText(f"*Ошибка подключения к серверу: {e}")
            if is_auto_login:
                self.clear_session()

    def main(self):
        if self.user_data and "username" in self.user_data:
            self.window_manager.show_main_window(self.user_data["username"])
        else:
            print("Ошибка: не удалось получить имя пользователя после входа")
