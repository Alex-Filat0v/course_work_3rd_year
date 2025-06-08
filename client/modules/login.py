import os
import sys
import json
import urllib.request
from hashlib import sha256
from PyQt6 import QtWidgets, uic


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        current_dir = os.path.dirname(__file__)
        file_dir = os.path.join(current_dir, "../templates/login.ui")
        uic.loadUi(file_dir, self)

        self.toolButton_login.clicked.connect(self.login)

    def login(self):
        username = self.lineEdit_login.text()
        password = self.lineEdit_password.text()
        remember_me = self.checkBox.isChecked()

        if username and password:

            password = sha256(password.encode('utf-8')).hexdigest()

            auth = {
                "username": username,
                "password": password,
            }

            data = json.dumps(auth).encode('utf-8')

            try:
                req = urllib.request.Request(
                    "http://127.0.0.1:8000/auth",
                    data=data,
                    headers={'Content-Type': 'application/json'}
                )
                opener = urllib.request.build_opener()

                with opener.open(req, timeout=10) as response:
                    status_code = response.getcode()

                if status_code == 200:
                    self.main()
                else:
                    self.label_error.setText(f"*Не верные имя пользователя или пароль")

            except Exception:
                self.label_error.setText(f"*Не верные имя пользователя или пароль")

        else:
            self.label_error.setText("*Обязательно заполните все поля для входа")

    def main(self):
        pass


if __name__ == "__main__":
    import asyncio

    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
