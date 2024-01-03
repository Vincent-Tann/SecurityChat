from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QLineEdit, QTableWidget, QTableWidgetItem, QDialog, QScrollArea
from MessageManager import MessageManager
from UserManager import UserManager
from Security import generate_key_pair, deserialization_key_pair, encrypt_message, generate_signature
import sys
from UI_Hacker import HackerWindow

def load_stylesheet(file_path):
    # 从文件加载样式表
    with open(file_path, "r", encoding='utf-8') as file:
        return file.read()
    
def main():
    app = QApplication(sys.argv)
    stylesheet = load_stylesheet("styleHacker.qss")
    app.setStyleSheet(stylesheet)

    user_manager = UserManager()
    message_manager = MessageManager()
    hacker_window = HackerWindow(user_manager, message_manager)
    hacker_window.show()
    app.exec_()

if __name__ == "__main__":
    main()