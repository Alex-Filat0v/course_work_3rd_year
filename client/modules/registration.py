import os
import sys
import json
import urllib.request
from hashlib import sha256
from datetime import datetime
from PyQt6 import QtWidgets, uic


class RegistrationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        current_dir = os.path.dirname(__file__)
        file_dir = os.path.join(current_dir, "../templates/registration.ui")
        uic.loadUi(file_dir, self)

        self.pushButton_registration.clicked.connect(self.try_registration)

    def try_registration(self):
        surname = self.lineEdit_surname.text()
        first_name = self.lineEdit_name.text()
        patronymic = self.lineEdit_patronymic.text()
        email = self.lineEdit_email.text()
        phone_number = self.lineEdit_number.text()
        date_of_birth = self.dateEdit.text()
        login = self.lineEdit_login.text()
        password = self.lineEdit_password.text()
        repeat_password = self.lineEdit_repeat_password.text()

        if password != repeat_password:
            self.label_error.setText("*Введенне вами пароли не совпадают")
            return

        try:
            date_of_birth = datetime.strptime(f"{date_of_birth}", "%Y-%m-%d").date()
            print(date_of_birth)
        except:
            date_of_birth = "2003-04-16"

        password = sha256(password.encode('utf-8')).hexdigest()

        auth = {
            "surname": surname,
            "first_name": first_name,
            "patronymic": patronymic,
            "mail": email,
            "phone_number": "+79528125252",
            "birth_date": date_of_birth,
            "username": login,
            "password": password
        }

        if not all(auth.values()):
            self.label_error.setText("*Обязательно заполните все поля для входа")
            return

        data = json.dumps(auth).encode('utf-8')

        try:

            req = urllib.request.Request(
                "http://127.0.0.1:8000/registrations",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            opener = urllib.request.build_opener()

            with opener.open(req, timeout=10) as response:
                status_code = response.getcode()

            if status_code == 200:
                self.label_error.setText("✅ Регистрация прошла успешно!")

        except Exception:
            self.label_error.setText(f"*Это имя пользователя уже занято!")



if __name__ == "__main__":

    import asyncio


    app = QtWidgets.QApplication(sys.argv)
    window = RegistrationWindow()
    window.show()
    sys.exit(app.exec())
