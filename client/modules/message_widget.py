from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt


class MessageWidget(QWidget):
    def __init__(self, message_id, author, text, timestamp, current_user, participants_count):
        super().__init__()
        self.message_id = message_id
        self.author = author
        self.current_user = current_user
        self.participants_count = participants_count

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 5, 8, 5)

        self.top_layout = QHBoxLayout()
        self.author_label = QLabel(f"<b>{author}</b>")
        self.timestamp_label = QLabel(timestamp)
        self.timestamp_label.setStyleSheet("color: grey;")

        self.top_layout.addWidget(self.author_label)
        self.top_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.top_layout.addWidget(self.timestamp_label)

        self.text_label = QLabel(text)
        self.text_label.setWordWrap(True)
        self.text_label.setMinimumHeight(20)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.text_label.setStyleSheet("color: black;")

        self.layout.addLayout(self.top_layout)
        self.layout.addWidget(self.text_label)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
