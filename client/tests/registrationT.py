import sys
from PyQt6 import QtWidgets, uic


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Регистрация.ui", self)
        self.pushButton_registration.clicked.connect(self.try_registration)
        self.pushButton_back.clicked.connect(self.back)

    def try_registration(self):
        last_name = self.lineEdit_surname.text()
        first_name = self.lineEdit_name.text()
        surname = self.lineEdit_patronymic.text()
        email = self.lineEdit_email.text()
        phone_number = self.lineEdit_number.text()
        date_of_birth = self.dateEdit.text()
        login = self.lineEdit_login.text()
        password = self.lineEdit_password.text()
        repeat_password = self.lineEdit_repeat_password.text()

        is_correct = True
        datas = [last_name, first_name, surname, email, phone_number, date_of_birth, login]
        for data in datas:
            if not data:
                is_correct = False
                break

        if is_correct and (password == repeat_password):
            print(f"Попытка регистрации: {datas}")
            # Тут делаем сверку с бд не заняты ли: логин, емаил и телефон
            # Если все ок записываем данные и регистрируем пользователя и перекидываем на страницу входа

        elif password != repeat_password:
            self.label_error.setText("*Введенне вами пароли не совпадают")

        else:
            self.label_error.setText("*Обязательно заполните все поля для входа")

    def back(self):
        print("Возвращаю на страницу входа")
        # Добавить логику закрытия текущего окнаи открытия окна входа


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
