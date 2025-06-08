import json
import sys
import os
import time
import random
from PyQt6 import uic, QtWidgets, QtCore, QtGui


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        current_dir = os.path.dirname(__file__)
        file_dir = os.path.join(current_dir, "../templates/main.ui")
        uic.loadUi(file_dir, self)

        self.pushButton_send_message.clicked.connect(self.send_message)
        self.lineEdit_message.returnPressed.connect(self.send_message)
        self.nick = "You"

    def accept_message(self):
        item = QtWidgets.QListWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        # Используем аватарку пользователя
        size = QtCore.QSize(45, 45)
        icon = QtGui.QIcon("../user_data/user.png")
        self.listWidget.setIconSize(size)
        item.setIcon(icon)

        item.setText(f"Иришка:\nВы там совсем абалдели ?")
        self.listWidget.addItem(item)

    def send_message(self):
        message_text = self.lineEdit_message.text()

        if message_text:
            # Добавляем свое сообщение в ListWidget
            item = QtWidgets.QListWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

            size = QtCore.QSize(45, 45)
            icon = QtGui.QIcon("../user_data/avatar.png")
            self.listWidget.setIconSize(size)
            item.setIcon(icon)

            # Выводим свое сообщение в панель и удаляем с поля воода
            item.setText(f"{self.nick} (ВЫ):\n{message_text}")
            self.listWidget.addItem(item)

            # Отчищаем строку ввода
            self.lineEdit_message.clear()

            self.accept_message()

        history = {}
        for i in range(10):
            symbol = random.randint(1, 1000)
            history[f"{i}"] = f"Иришка:\n{symbol}"
        print(history)

        #self.load_history(history)

        # обавить отображение сообщения в чате
        # Отправлять текст сообщения на сервер, обнавляя чат у каждого участника

    def load_history(self, history: dict):
        print(self.nick)
        for item in history:

            # Добавляем свое сообщение в ListWidget
            item = QtWidgets.QListWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

            size = QtCore.QSize(45, 45)
            icon = QtGui.QIcon("../user_data/user.png")
            self.listWidget.setIconSize(size)
            item.setIcon(icon)

            # Выводим свое сообщение в панель и удаляем с поля воода
            item.setText(f"{history.get(item)}")
            self.listWidget.addItem(item)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
