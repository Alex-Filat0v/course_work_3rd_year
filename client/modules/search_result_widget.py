from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal


class SearchResultWidget(QWidget):
    add_contact_requested = pyqtSignal(str)

    def __init__(self, user_data: dict, parent=None):
        super().__init__(parent)
        self.username_to_add = user_data.get('username')

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        info_text = f"{user_data.get('first_name')} {user_data.get('surname')} ({self.username_to_add})"
        info_label = QLabel(info_text)

        self.add_button = QPushButton("➕")
        self.add_button.setToolTip("Добавить в контакты")
        self.add_button.setFixedSize(30, 30)
        self.add_button.clicked.connect(self.on_add_clicked)

        layout.addWidget(info_label)
        layout.addStretch()
        layout.addWidget(self.add_button)

    def on_add_clicked(self):
        print(f"Запрос на добавление контакта: {self.username_to_add}")
        self.add_contact_requested.emit(self.username_to_add)
        self.add_button.setText("✔️")
        self.add_button.setEnabled(False)
