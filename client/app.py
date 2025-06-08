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

        # Показываем начальное окно
        self.login_window.show()

    def show_login(self):
        self.registration_window.close()
        self.login_window.show()

    def show_registration(self):
        self.login_window.close()
        self.registration_window.show()

    def show_main_window(self):
        try:
            self.login_window.close()
            self.registration_window.close()
        finally:
            self.main_window.show()


class LogWindow(LoginWindow):
    def __init__(self, window_manager):
        super().__init__()
        self.window_manager = window_manager
        self.toolButton_registration.clicked.connect(self.register)

    def register(self):
        self.window_manager.show_registration()

    def main(self):
        self.window_manager.show_main_window()


class RegWindow(RegistrationWindow):
    def __init__(self, window_manager):
        super().__init__()
        self.window_manager = window_manager
        self.pushButton_back.clicked.connect(self.back)

    def back(self):
        self.window_manager.show_login()


class MWindow(MainWindow):
    def __init__(self, window_manager):
        super().__init__()
        self.window_manager = window_manager


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    manager = WindowManager()
    sys.exit(app.exec())
