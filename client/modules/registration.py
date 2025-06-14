import os
import sys
import requests
from hashlib import sha256
from PyQt6 import QtWidgets, uic, QtCore


class RegistrationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(__file__)
        file_dir = os.path.join(current_dir, "../templates/registration.ui")
        uic.loadUi(file_dir, self)

        self.pushButton_registration.clicked.connect(self.try_registration)
        self.dateEdit.setDate(QtCore.QDate.currentDate())

    def try_registration(self):
        surname = self.lineEdit_surname.text().strip()
        first_name = self.lineEdit_name.text().strip()
        patronymic = self.lineEdit_patronymic.text().strip()
        email = self.lineEdit_email.text().strip()
        phone_number = self.lineEdit_number.text().strip()
        date_of_birth_str = self.dateEdit.date().toString("yyyy-MM-dd")
        login = self.lineEdit_login.text().strip()
        password = self.lineEdit_password.text()
        repeat_password = self.lineEdit_repeat_password.text()

        if not all([surname, first_name, email, phone_number, login, password]):
            self.label_error.setText("*Обязательно заполните все поля")
            return

        if password != repeat_password:
            self.label_error.setText("*Введенные вами пароли не совпадают")
            return
        elif len(password) < 5:
            self.label_error.setText("*Введенный вами пароль слишком простой")
            return
        elif len(login) < 4:
            self.label_error.setText("*Введенный вами логин слишком короткий")
            return

        hashed_password = sha256(password.encode('utf-8')).hexdigest()

        registration_data = {
            "surname": surname,
            "first_name": first_name,
            "patronymic": patronymic,
            "mail": email,
            "phone_number": phone_number,
            "birth_date": date_of_birth_str,
            "username": login,
            "password": hashed_password
        }

        try:
            response = requests.post(
                "http://127.0.0.1:8000/registrations",
                json=registration_data,
                timeout=10
            )

            if response.status_code == 200:
                self.label_error.setText("✅ Регистрация прошла успешно! Теперь вы можете войти.")

            else:
                error_detail = response.json().get('detail', 'Неизвестная ошибка сервера.')
                self.label_error.setText(f"*{error_detail[0].get("msg")}")

        except requests.exceptions.RequestException:
            self.label_error.setStyleSheet("color: red;")
            self.label_error.setText(f"*Ошибка подключения к серверу. Попробуйте позже.")
