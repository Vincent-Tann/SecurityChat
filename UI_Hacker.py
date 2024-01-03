from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QLineEdit, QTableWidget, QTableWidgetItem, QDialog, QScrollArea
from PySide2.QtGui import QIcon
from MessageManager import MessageManager
from UserManager import UserManager
from Security import generate_key_pair, deserialization_key_pair, encrypt_message, generate_signature
import base64

class HackerWindow(QWidget):
    def __init__(self, user_manager, message_manager):
        super().__init__()
        self.user_manager = user_manager
        self.message_manager = message_manager
        self.initUI()

    def initUI(self):
        self.resize(830, 300)
        self.setWindowTitle('Hacker Interface')
        self.setWindowIcon(QIcon('img/hacker_icon.png'))
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget(self)
        self.table.setColumnCount(6)  # 发送者、接收者、时间、密文、数字签名、操作
        self.table.setHorizontalHeaderLabels(['发送者', '接收者', '时间', '密文', '数字签名', '操作'])
        self.layout.addWidget(self.table)

        self.load_messages()

    def load_messages(self):
        messages = self.message_manager.messages
        self.table.setRowCount(len(messages))
        for i, msg in enumerate(messages):
            self.table.setItem(i, 0, QTableWidgetItem(msg['sender']))
            self.table.setItem(i, 1, QTableWidgetItem(msg['receiver']))
            self.table.setItem(i, 2, QTableWidgetItem(msg['timestamp']))
            self.table.setItem(i, 3, QTableWidgetItem(msg['encrypted_message']))
            self.table.setItem(i, 4, QTableWidgetItem(msg['signature']))
            btn_edit = QPushButton('修改')
            # btn_edit.clicked.connect(lambda _, row=i: self.edit_message(row))
            btn_edit.clicked.connect(lambda: self.edit_message(i))
            self.table.setCellWidget(i, 5, btn_edit)

    def edit_message(self, row):
        edit_dialog = EditMessageDialog(self, self.message_manager, row)
        edit_dialog.exec_()
        self.load_messages()  # 刷新消息列表

class EditMessageDialog(QDialog):
    def __init__(self, parent, message_manager, row):
        super().__init__(parent)
        self.message_manager = message_manager
        self.row = row
        self.message = message_manager.messages[row]
        self.user_manager = UserManager()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Edit Message')
        layout = QVBoxLayout(self)

        # 显示消息的详细信息
        self.sender_label = QLabel(f'发送者: {self.message["sender"]}')
        self.receiver_label = QLabel(f'接收者: {self.message["receiver"]}')
        self.timestamp_label = QLabel(f'时间: {self.message["timestamp"]}')
        # self.encrypted_message_label = QLabel(f'密文: {self.message["encrypted_message"]}')
        # self.signature_label = QLabel(f'数字签名: {self.message["signature"]}')
        layout.addWidget(self.sender_label)
        layout.addWidget(self.receiver_label)
        layout.addWidget(self.timestamp_label)
        # layout.addWidget(self.encrypted_message_label)
        # layout.addWidget(self.signature_label)

        # 密文标签和滚动区域
        self.encrypted_message_label = QLabel(f'密文: {self.message["encrypted_message"]}')
        encrypted_scroll_area = QScrollArea()
        encrypted_scroll_area.setWidgetResizable(True)
        encrypted_scroll_area.setWidget(self.encrypted_message_label)
        layout.addWidget(encrypted_scroll_area)

        # 数字签名标签和滚动区域
        self.signature_label = QLabel(f'数字签名: {self.message["signature"]}')
        signature_scroll_area = QScrollArea()
        signature_scroll_area.setWidgetResizable(True)
        signature_scroll_area.setWidget(self.signature_label)
        layout.addWidget(signature_scroll_area)

        # 输入框用于输入修改后的明文
        self.plain_message_input = QLineEdit(self)
        layout.addWidget(self.plain_message_input)

        # 修改按钮
        self.edit_button = QPushButton('修改', self)
        self.edit_button.clicked.connect(self.edit_message)
        layout.addWidget(self.edit_button)

    def edit_message(self):
        # 读取收发人
        sender = self.message['sender']
        receiver = self.message['receiver']
        # 读取接受者公钥
        receiver_public_pem = self.user_manager.users[receiver]['public_key'].encode('utf-8')
        receiver_public_key, _ = deserialization_key_pair(receiver_public_pem, None)
        # 模拟加密结果
        message_text = self.plain_message_input.text()
        new_encrypted_message = encrypt_message(message_text, receiver_public_key)
        # 只能使用黑客自己的私钥
        _, hacker_private_key = generate_key_pair()
        # 模拟签名的结果
        new_signature = generate_signature(new_encrypted_message, hacker_private_key)

        # 更新消息
        self.message_manager.messages[self.row]['encrypted_message'] = base64.b64encode(new_encrypted_message).decode('utf-8')
        self.message_manager.messages[self.row]['signature'] = base64.b64encode(new_signature).decode('utf-8')
        self.message_manager.save_messages()

        QMessageBox.information(self, '消息', '消息已修改。')
        self.accept()


# 主函数
if __name__ == '__main__':
    app = QApplication([])

    user_manager = UserManager()
    message_manager = MessageManager()
    hacker_window = HackerWindow(user_manager, message_manager)
    hacker_window.show()
    app.exec_()
