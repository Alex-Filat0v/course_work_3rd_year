from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt


def insert_word_breaks(text, interval=20):
    def break_long_word(word):
        if len(word) <= interval:
            return word
        return '\u200b'.join(word[i:i + interval] for i in range(0, len(word), interval))

    return ' '.join(break_long_word(word) for word in text.split(' '))


class MessageWidget(QWidget):
    def __init__(self, message_id, author, text, timestamp, current_user, participants_count):
        super().__init__()

        self.message_id = message_id
        self.author = author
        self.current_user = current_user
        self.participants_count = participants_count

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 6, 10, 6)
        self.layout.setSpacing(4)

        self.top_layout = QHBoxLayout()
        self.top_layout.setContentsMargins(0, 0, 0, 0)

        self.author_label = QLabel(f"<b>{author}</b>")
        self.author_label.setStyleSheet("font-size: 12pt;")
        self.author_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.timestamp_label = QLabel(f"<b>{timestamp}</b>")
        self.timestamp_label.setStyleSheet("font-size: 11pt; color: black;")
        self.timestamp_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.timestamp_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.top_layout.addWidget(self.author_label)
        self.top_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.top_layout.addWidget(self.timestamp_label)

        processed_text = str(insert_word_breaks(text))

        self.text_label = QLabel(processed_text)
        self.text_label.setWordWrap(True)
        self.text_label.setMaximumWidth(980)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.text_label.setStyleSheet("font-size: 12pt; padding: 4px; color: black;")

        self.layout.addLayout(self.top_layout)
        self.layout.addWidget(self.text_label)

        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
