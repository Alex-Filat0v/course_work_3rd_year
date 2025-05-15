import sys
from PyQt6 import QtWidgets, uic


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("вход.ui", self)
        self.toolButton_login.clicked.connect(self.login)
        self.toolButton_registration.clicked.connect(self.register)

    def login(self):
        username = self.lineEdit_login.text()
        password = self.lineEdit_password.text()
        remember_me = self.checkBox.isChecked()

        if username and password:
            print(f"Попытка входа:\nЛогин: {username}\nПароль: {password}\nЗапомнить меня: {remember_me}")
            # Тут делаем сверку с бд и если пользователь есть закрваем окно с входа и открваем главное окно

        else:
            self.label_error.setText("*Обязательно заполните все поля для входа")

    def register(self):
        print("Открытие окна регистрации")
        # Тут закрваем текущее окно и открваем окно регистрации


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
