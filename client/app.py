import sys
from PyQt6 import QtWidgets
from modules.login import LoginWindow
from modules.registration import RegistrationWindow
from modules.main_window import MainWindow


class WindowManager:
    def __init__(self):
        self.login_window = LogWindow(self)
        self.registration_window = RegWindow(self)
        self.main_window = MWindow(self)

    def start(self):
        self.login_window.load_and_login()

        if not self.login_window.user_data:
            self.login_window.show()

    def show_login(self):
        self.registration_window.close()
        self.main_window.close()
        self.login_window.show()

    def show_registration(self):
        self.login_window.close()
        self.registration_window.show()

    def show_main_window(self, username: str):
        try:
            self.login_window.close()
            self.registration_window.close()
        finally:
            self.main_window.show()
            self.main_window.initialize_user(username)


class LogWindow(LoginWindow):
    def __init__(self, window_manager):
        super().__init__()
        self.window_manager = window_manager
        self.toolButton_registration.clicked.connect(self.register)
        self.user_data = {}

    def register(self):
        self.window_manager.show_registration()

    def main(self):
        if self.user_data and "username" in self.user_data:
            self.window_manager.show_main_window(self.user_data["username"])
        else:
            print("Ошибка: не удалось получить имя пользователя после входа")


class RegWindow(RegistrationWindow):
    def __init__(self, window_manager):
        super().__init__()
        self.window_manager = window_manager
        try:
            self.pushButton_back.clicked.connect(self.back)
        except AttributeError:
            print("ВНИМАНИЕ: Кнопка 'Назад' (pushButton_back) не найдена в registration.ui")

    def back(self):
        self.window_manager.show_login()


class MWindow(MainWindow):
    def __init__(self, window_manager):
        super().__init__()
        self.window_manager = window_manager


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    manager = WindowManager()
    manager.start()
    sys.exit(app.exec())
