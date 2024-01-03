from PySide2.QtWidgets import QApplication
from UI_LoginRegister import LoginWindow, RegisterWindow
from UserManager import UserManager
import sys

def load_stylesheet(file_path):
    # 从文件加载样式表
    with open(file_path, "r", encoding='utf-8') as file:
        return file.read()
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    stylesheet = load_stylesheet("style.qss")
    app.setStyleSheet(stylesheet)

    user_manager = UserManager()  # 实例化用户管理
    login_window = LoginWindow(user_manager)
    login_window.show()

    app.exec_()
