from PySide2.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QListWidget, QListWidgetItem, QTextEdit, QPushButton,
                               QLabel, QLineEdit, QFrame)
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt
from UserManager import UserManager
from MessageManager import MessageManager
from Security import encrypt_message, decrypt_message, generate_signature, verify_signature, deserialization_key_pair
import datetime
import base64

from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout

class ContactItemWidget(QWidget):
    def __init__(self, username, last_message):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # 用户名标签
        self.username = username
        self.name_label = QLabel(username)
        self.name_label.setStyleSheet("font-size: 12pt; font-weight: bold; background-color: transparent")  # 大字体，加粗
        self.layout.addWidget(self.name_label)

        # 聊天记录标签
        self.message_label = QLabel(last_message)
        self.message_label.setStyleSheet("font-size: 10pt; background-color: transparent")  # 小字体
        self.layout.addWidget(self.message_label)

        # self.setStyleSheet("border-bottom: 1px solid gray;")  # 灰色分隔线
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separator)


class ChatWindow(QWidget):
    def __init__(self, user, use_signature=True):
        super().__init__()
        self.user_manager = UserManager()
        self.message_manager = MessageManager()
        self.user = user
        self.use_signature = use_signature
        self.current_chat = None
        self.initUI()
        print("Chat init success.")
        print(f"username: {user}")

    def initUI(self):
        self.setWindowTitle(f"SecurityChat - {self.user}")
        self.setWindowIcon(QIcon('img/app_icon.png'))
        self.resize(800, 600)

        # Horizontal layout for the whole window
        self.layout = QHBoxLayout(self)

        # List of contacts on the left
        self.contacts_list = QListWidget(self)
        self.contacts_list.setMaximumWidth(200)
        self.layout.addWidget(self.contacts_list)

        # Chat display and input on the right
        self.chat_layout = QVBoxLayout()
        
        # Where chat messages will be displayed
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_layout.addWidget(self.chat_display)

        # Message input area
        self.message_input = QLineEdit(self)
        self.chat_layout.addWidget(self.message_input)
        self.message_input.returnPressed.connect(self.send_message) #按回车发送

        # Send button
        self.send_button = QPushButton('发送', self)
        self.chat_layout.addWidget(self.send_button)

        # Add the right column layout to the main layout
        self.layout.addLayout(self.chat_layout)

        # Populate contacts list for demonstration purposes
        self.populate_contacts()

        # Connect buttons and list items to functions
        self.send_button.clicked.connect(self.send_message)
        self.contacts_list.itemClicked.connect(self.select_chat)

    def populate_contacts(self):
        self.contacts_list.clear()
        # 左侧按列表显示不同联系人
        for user in self.user_manager.users: #键名就是username
            if user == self.user:
                continue
            # item = QListWidgetItem(user)
            # self.contacts_list.addItem(item)

            # 假设 getLastMessage 方法返回与该用户的最后一条消息
            last_message = self.getLastMessage(user)

            # 创建自定义列表项控件
            contact_widget = ContactItemWidget(user, last_message)

            # 创建 QListWidgetItem
            item = QListWidgetItem()
            self.contacts_list.addItem(item)

            # 设置自定义列表项的大小
            item.setSizeHint(contact_widget.sizeHint())

            # 将自定义控件添加到 QListWidgetItem
            self.contacts_list.setItemWidget(item, contact_widget)
            
    def getLastMessage(self, chatter):
        messages = self.message_manager.get_messages_between_users(self.user, chatter)
        if len(messages)==0:
            return ""
        last_message = self.message_manager.get_plain_message(messages[-1], self.user)
        return last_message

    def select_chat(self):
        # 获取当前选中的 QListWidgetItem
        current_item = self.contacts_list.currentItem()

        if current_item is not None:
            # 获取与 QListWidgetItem 相关联的 ContactItemWidget
            contact_widget = self.contacts_list.itemWidget(current_item)
            # 从 ContactItemWidget 获取用户名
            self.current_chat = contact_widget.username

        self.chat_display.clear()
        self.message_manager = MessageManager() # 刷新读取
        messages = self.message_manager.get_messages_between_users(self.user, self.current_chat)
        self.display_messages(messages)

        self.populate_contacts()


    def display_messages(self, messages):
        # 逐条显示按时间顺序排好的消息
        for message in messages:
            self.add_message_to_display(message)

    def send_message(self):
        # 读取输入的文字并显示
        message_text = self.message_input.text()
        timestamp = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        message = {
            'sender': self.user,
            'receiver:': self.current_chat,
            'timestamp': timestamp,
            'plain_message': message_text,
        }
        self.add_message_to_display(message)
        # 用对方的公钥加密信息
        receiver_public_pem = self.user_manager.users[self.current_chat]['public_key'].encode('utf-8')
        receiver_public_key, _ = deserialization_key_pair(receiver_public_pem, None)
        encrypted_message = encrypt_message(message_text, receiver_public_key)
        # encrypted_message_base64 = base64.b64encode(encrypted_message).decode('utf-8')
        # 使用发送者自己的私钥得到加密信息的数字签名
        sender_private_pem = self.user_manager.users[self.user]['private_key'].encode('utf-8')
        _, sender_private_key = deserialization_key_pair(None, sender_private_pem)
        signature = generate_signature(encrypted_message, sender_private_key)
        # 将加密后的信息和数字签名保存到信息库（发送到服务器）
        self.message_manager.add_message(sender=self.user, receiver=self.current_chat, timestamp=timestamp, encrypted_message=encrypted_message, plain_message=message_text, signature=signature)
        # 清空输入框
        self.message_input.clear()

        # 更新联系人列表
        self.populate_contacts()

    def add_message_to_display(self, message):
        time = message['timestamp']
        # plain_message = self.message_manager.get_plain_message(message, self.user)
        if message['sender'] == self.user:
            # 自己发送的消息在右边显示
            self.chat_display.setAlignment(Qt.AlignRight)
            # 无法访问对方私钥，好像没法自己解密自己发送的加密消息。。。
            # self.chat_display.append(f"{time}\n我: {message['plain_message']}\n")
            # self.chat_display.append(f"{time}<br><font size='4'>我: {message['plain_message']}</font><br>")
            self.chat_display.append(f"<div style='text-align: right;'>{time}<br><font size='4'>我: {message['plain_message']}</font></div><br>")
            # self.chat_display.append(f"{time}\n我: {plain_message}\n")
        else:
            # 如果是其他人发送的消息，则在左边显示
            self.chat_display.setAlignment(Qt.AlignLeft)
            # 用自己的私钥解密消息
            private_pem = self.user_manager.users[self.user]['private_key'].encode('utf-8')
            _, private_key = deserialization_key_pair(None, private_pem)
            encrypted_message = message['encrypted_message']
            plain_message = decrypt_message(base64.b64decode(encrypted_message), private_key)
            # self.chat_display.append(f"{time}\n{message['sender']}: {plain_message}")
            # self.chat_display.append(f"{time}<br><font size='4'>{message['sender']}: {plain_message}</font><br>")
            message_to_show = f"<div style='text-align: left;'>{time}<br><font size='4'>{message['sender']}: {plain_message}</font></div>"
            # self.chat_display.append(message_to_show)
            # self.chat_display.append(f"<div style='text-align: left;'>{time}<br><font size='4'>{message['sender']}: {plain_message}</font></div><br>")
            # 验证数字签名
            encrypt_message = base64.b64decode(message['encrypted_message'])
            signature = base64.b64decode(message['signature'])
            sender_public_pem = self.user_manager.users[message['sender']]['public_key'].encode('utf-8')
            sender_public_key, _ = deserialization_key_pair(sender_public_pem, None)
            pass_verification = verify_signature(encrypt_message, signature, sender_public_key)
            note_color = "green" if pass_verification else "red"
            # note = "<font color='green'>[此条消息已通过对方的数字签名验证]</font><br>" if pass_verification else f"<font color='{note_color}'>---此条消息未通过对方的数字签名验证，消息被篡改！---</font><br>"
            note = f"<div style='text-align: left;'><font color='{note_color}'>[此条消息已通过对方的数字签名验证]</font></div><br>" if pass_verification else f"<div style='text-align: left;'><font color='{note_color}'>[此条消息未通过对方的数字签名验证，消息被篡改！]</font></div><br>"
            
            if self.use_signature:
                self.chat_display.append(message_to_show + note)
            else:
                self.chat_display.append(message_to_show + "<br>")

if __name__ == '__main__':
    app = QApplication([])

    # UserManager would be instantiated here
    user = "Vincent"  # Replace with actual UserManager
    use_signature = False
    chat_window = ChatWindow(user)
    chat_window.show()

    app.exec_()
