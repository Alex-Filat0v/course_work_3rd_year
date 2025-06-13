import os
import requests
from PyQt6 import QtWidgets, uic, QtCore


class CreateGroupWindow(QtWidgets.QMainWindow):
    group_created = QtCore.pyqtSignal()

    def __init__(self, current_user: str, parent=None):
        super().__init__(parent)
        self.current_user = current_user

        current_dir = os.path.dirname(__file__)
        file_dir = os.path.join(current_dir, "../templates/create_group.ui")
        uic.loadUi(file_dir, self)

        self.setWindowTitle("Создание новой группы")

        self.lineEdit_title.setStyleSheet("color: black;")
        self.listWidget_contacts.setStyleSheet("""
            QListWidget {
                background-color: white; 
                border-radius: 5px;
            }
            QCheckBox { 
                color: black; /* Цвет текста для чекбоксов */
            }
        """)

        self.pushButton_add_group.clicked.connect(self.create_group)

        self.load_contacts()

    def load_contacts(self):
        self.listWidget_contacts.clear()
        try:
            response = requests.get(f"http://127.0.0.1:8000/contacts/{self.current_user}")
            if response.status_code == 200:
                contacts = response.json()
                for contact in contacts:
                    item = QtWidgets.QListWidgetItem(self.listWidget_contacts)
                    checkbox = QtWidgets.QCheckBox(
                        f"{contact['first_name']} {contact['surname']} ({contact['username']})")
                    checkbox.setProperty("username", contact['username'])
                    self.listWidget_contacts.addItem(item)
                    self.listWidget_contacts.setItemWidget(item, checkbox)
            else:
                self.label_error.setText("Ошибка загрузки контактов.")
        except requests.RequestException:
            self.label_error.setText("Ошибка сети.")

    def create_group(self):
        group_title = self.lineEdit_title.text().strip()
        if not group_title:
            self.label_error.setText("Введите название группы.")
            return

        selected_participants = [self.current_user]
        for i in range(self.listWidget_contacts.count()):
            item = self.listWidget_contacts.item(i)
            checkbox = self.listWidget_contacts.itemWidget(item)
            if checkbox.isChecked():
                selected_participants.append(checkbox.property("username"))

        if len(selected_participants) < 2:
            self.label_error.setText("Выберите хотя бы одного участника.")
            return

        request_data = {
            "title": group_title,
            "participants": selected_participants,
            "creator": self.current_user
        }

        try:
            response = requests.post("http://127.0.0.1:8000/chats/group", json=request_data)
            if response.status_code == 200:
                print("Группа успешно создана!")
                self.group_created.emit()
                self.close()
            else:
                error_msg = response.json().get('detail', 'Неизвестная ошибка')
                self.label_error.setText(f"Ошибка: {error_msg}")
        except requests.RequestException:
            self.label_error.setText("Ошибка сети при создании группы.")
