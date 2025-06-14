import json
import os
import asyncio
import threading
import requests
import websockets
from datetime import datetime
from PyQt6 import uic, QtWidgets, QtCore

from .message_widget import MessageWidget
from .create_group import CreateGroupWindow
from .search_result_widget import SearchResultWidget


class MessageReceiver(QtCore.QObject):
    message_received = QtCore.pyqtSignal(str)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        current_dir = os.path.dirname(__file__)
        file_dir = os.path.join(current_dir, "../templates/main.ui")
        uic.loadUi(file_dir, self)

        self.listView.setEnabled(False)

        search_style = "color: black; background-color: white; border-radius: 5px; padding-left: 5px;"
        self.lineEdit_search_chat.setStyleSheet(search_style)
        self.lineEdit_message.setStyleSheet(
            "color: white; background-color: #353535; border-radius: 5px; padding: 5px;")

        self.proxyButton_search_chat.clicked.connect(lambda: self.lineEdit_search_chat.setFocus())

        self.window_manager = None
        self.nick = "User"

        self.ws_client = None
        self.loop = None
        self.is_running = False
        self.chats = {}
        self.current_chat_id = None

        self.pushButton_send_message.clicked.connect(self.send_message)
        self.lineEdit_message.returnPressed.connect(self.send_message)
        self.comboBox_menu_accaunt.currentIndexChanged.connect(self.handle_account_menu)
        self.listWidget_1.itemClicked.connect(self.on_chat_selected)
        self.listWidget_2.itemClicked.connect(self.on_chat_selected)
        self.toolButton_add_group.clicked.connect(self.open_create_group_dialog)
        self.lineEdit_search_chat.textChanged.connect(self.on_search_text_changed)

        self.receiver = MessageReceiver()
        self.receiver.message_received.connect(self.display_incoming_message)

        self.listWidget.setStyleSheet("""
            QListWidget {
                border: 1px solid #353535;
                background-color: #404040;
            } 
            QListWidget::item {
                color: black; padding: 0px; margin: 0px; border: none;
            }
            QListWidget::item:selected, QListWidget::item:hover {
                background-color: transparent; border: none;
            }
        """)
        self.listWidget.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.lineEdit_search_chat.raise_()

    def initialize_user(self, username: str):
        self.nick = username
        self.load_user_chats()

    def load_user_chats(self):
        self.chats.clear()
        try:
            response = requests.get(f"http://127.0.0.1:8000/chats/{self.nick}")
            if response.status_code == 200:
                chats_data = response.json()

                for chat in chats_data:
                    chat_id = chat['_id']
                    self.chats[chat_id] = chat

                self.display_group_chats()
                self.display_private_chats()

                if chats_data:
                    first_chat_id = chats_data[0]['_id']
                    self.switch_to_chat(first_chat_id)
                else:
                    print("У пользователя нет чатов.")
                    self.listWidget.clear()
                    self.toolButton_info_group.setText("Выберите или создайте чат")

            else:
                print(f"Ошибка загрузки чатов: {response.text}")
        except requests.RequestException as e:
            print(f"Ошибка подключения к серверу: {e}")

    def on_chat_selected(self, item):
        chat_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if chat_id and chat_id != self.current_chat_id:
            if self.lineEdit_search_chat.text():
                self.lineEdit_search_chat.clear()
            self.switch_to_chat(chat_id)
        else:
            print("Клик по элементу без ID (результат поиска)")

    def switch_to_chat(self, chat_id):
        print(f"Переключение на чат: {chat_id}")

        if hasattr(self, 'ws_thread') and self.ws_thread.is_alive():
            print("Останавливаем предыдущий поток WebSocket...")
            self.is_running = False
            self.ws_thread.join(timeout=1.0)
            if self.ws_thread.is_alive():
                print("ВНИМАНИЕ: Предыдущий поток не завершился вовремя.")

        self.current_chat_id = chat_id
        chat_info = self.chats.get(chat_id)
        if chat_info:
            title = chat_info.get('title') or next((p for p in chat_info['participants'] if p != self.nick), "Чат")
            self.toolButton_info_group.setText(title)

        self.load_history()

        self.is_running = True
        self.ws_thread = threading.Thread(target=self.run_websocket_client, args=(chat_id,))
        self.ws_thread.daemon = True
        self.ws_thread.start()

    def load_history(self):
        self.listWidget.clear()
        if not self.current_chat_id: return
        try:
            response = requests.get(f"http://127.0.0.1:8000/chats/history/{self.current_chat_id}")
            if response.status_code == 200:
                history = response.json()
                for msg in history:
                    self.add_message_to_widget(msg)

            else:
                system_msg = {"author_username": "System", "text": f"Ошибка загрузки истории: {response.status_code}",
                              "created_at": datetime.now().isoformat()}
                self.add_message_to_widget(system_msg)
        except requests.RequestException as e:
            system_msg = {"author_username": "System", "text": f"Ошибка подключения: {e}",
                          "created_at": datetime.now().isoformat()}
            self.add_message_to_widget(system_msg)

    def run_websocket_client(self, chat_id):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        async def client_logic():
            uri = f"ws://127.0.0.1:8000/ws/{chat_id}/{self.nick}"
            while self.is_running:
                try:
                    async with websockets.connect(uri) as websocket:
                        self.ws_client = websocket
                        while self.is_running:
                            try:
                                message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                                self.receiver.message_received.emit(message)
                            except asyncio.TimeoutError:
                                continue
                            except websockets.exceptions.ConnectionClosed:
                                self.is_running = False
                                break
                except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError, OSError):
                    if self.is_running: await asyncio.sleep(5)
                except Exception as e:
                    print(f"Неизвестная ошибка в WebSocket потоке: {e}")
                    self.is_running = False

        self.loop.run_until_complete(client_logic())
        print(f"Поток WebSocket для чата {chat_id} завершил работу.")

    def send_message(self):
        message_text = self.lineEdit_message.text().strip()
        if message_text and self.ws_client and self.loop and self.current_chat_id:
            message_to_send = {"type": "text_message", "text": message_text}
            asyncio.run_coroutine_threadsafe(self.ws_client.send(json.dumps(message_to_send)), self.loop)
            self.lineEdit_message.clear()

    def display_incoming_message(self, message_json: str):
        try:
            data = json.loads(message_json)
            msg_type = data.get("type")

            if msg_type == "new_message":
                if data.get("author_username") == self.nick:
                    print("Получено эхо собственного сообщения. Игнорируем отображение.")
                    pass

                if data.get('chat_id') == self.current_chat_id:
                    self.add_message_to_widget(data)

        except json.JSONDecodeError:
            print(f"Получено некорректное JSON-сообщение: {message_json}")

    def add_message_to_widget(self, msg_data):
        message_id = msg_data.get('_id', 'system_msg')
        author = msg_data.get('author_username', 'System')
        text = msg_data.get('text', '')
        try:
            timestamp_dt = datetime.fromisoformat(msg_data['created_at'])
            time_str = timestamp_dt.strftime("%d.%m.%y %H:%M")
        except (ValueError, TypeError, KeyError):
            time_str = ""
        chat_info = self.chats.get(self.current_chat_id, {})
        participants_count = len(chat_info.get('participants', []))

        message_item_widget = MessageWidget(message_id, author, text, time_str, self.nick, participants_count)
        list_item = QtWidgets.QListWidgetItem(self.listWidget)
        list_item.setSizeHint(message_item_widget.sizeHint())

        if author == self.nick:
            message_item_widget.setStyleSheet("background-color: #d9dffc; border-radius: 5px;")
        else:
            message_item_widget.setStyleSheet("background-color: #838ec7; border-radius: 5px;")

        self.listWidget.addItem(list_item)
        self.listWidget.setItemWidget(list_item, message_item_widget)
        self.listWidget.scrollToBottom()

    def on_search_text_changed(self, text: str):
        query = text.strip()
        if len(query) >= 2:
            self.search_for_contacts(query)
        else:
            if not self.is_private_chats_displayed():
                self.display_private_chats()

    def is_private_chats_displayed(self):
        if self.listWidget_2.count() == 0:
            return True
        item = self.listWidget_2.item(0)
        if item and item.data(QtCore.Qt.ItemDataRole.UserRole):
            return True
        return False

    def search_for_contacts(self, query: str):
        self.listWidget_2.clear()
        try:
            params = {"current_user": self.nick, "query": query}
            response = requests.get("http://127.0.0.1:8000/users/search", params=params)

            if response.status_code == 200:
                users = response.json()
                if not users:
                    self.listWidget_2.addItem("Ничего не найдено")
                else:
                    for user in users:
                        list_item = QtWidgets.QListWidgetItem(self.listWidget_2)
                        widget = SearchResultWidget(user)
                        widget.add_contact_requested.connect(self.add_contact)
                        list_item.setSizeHint(widget.sizeHint())
                        self.listWidget_2.addItem(list_item)
                        self.listWidget_2.setItemWidget(list_item, widget)
            else:
                self.listWidget_2.addItem(f"Ошибка поиска: {response.status_code}")
        except requests.RequestException:
            self.listWidget_2.addItem("Ошибка сети")

    @QtCore.pyqtSlot(str)
    def add_contact(self, contact_username: str):
        try:
            add_response = requests.post(f"http://127.0.0.1:8000/contacts/{self.nick}/add/{contact_username}")

            if add_response.status_code == 201 or (
                    add_response.status_code == 400 and "already exists" in add_response.text):

                print(f"Контакт {contact_username} добавлен/существует. Создаем личный чат...")
                chat_response = requests.post(f"http://127.0.0.1:8000/chats/direct/{self.nick}/{contact_username}")

                if chat_response.status_code == 200:
                    QtWidgets.QMessageBox.information(self, "Успех",
                                                      f"Чат с пользователем {contact_username} готов!")
                    self.load_user_chats()
                else:
                    error = chat_response.json().get('detail', 'Не удалось создать личный чат')
                    QtWidgets.QMessageBox.warning(self, "Ошибка", error)

            else:
                error = add_response.json().get('detail', 'Не удалось добавить контакт')
                QtWidgets.QMessageBox.warning(self, "Ошибка", error)

        except requests.RequestException:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Ошибка сети при добавлении контакта.")

    def display_group_chats(self):

        self.listWidget_1.clear()
        for chat_id, chat in self.chats.items():
            if chat['is_group_chat']:
                item = QtWidgets.QListWidgetItem()
                item.setData(QtCore.Qt.ItemDataRole.UserRole, chat_id)
                item.setText(chat.get('title', 'Групповой чат'))
                self.listWidget_1.addItem(item)

    def display_private_chats(self):
        self.lineEdit_search_chat.setText("")
        self.listWidget_2.clear()
        for chat_id, chat in self.chats.items():
            if not chat['is_group_chat']:
                item = QtWidgets.QListWidgetItem()
                item.setData(QtCore.Qt.ItemDataRole.UserRole, chat_id)
                other_user = next((p for p in chat['participants'] if p != self.nick), "Unknown")
                item.setText(other_user)
                self.listWidget_2.addItem(item)

    def open_create_group_dialog(self):
        dialog = CreateGroupWindow(self.nick, self)
        dialog.group_created.connect(self.on_group_created)
        dialog.show()

    @QtCore.pyqtSlot()
    def on_group_created(self):
        print("Получен сигнал о создании группы, обновляем список чатов...")
        self.load_user_chats()

    def handle_account_menu(self, index):
        self.comboBox_menu_accaunt.setCurrentIndex(0)
        if index == 1:
            self.logout()

    def logout(self):
        print("Выход из системы...")
        self.is_running = False
        if self.window_manager:
            self.window_manager.login_window.clear_session()
            self.window_manager.show_login()
