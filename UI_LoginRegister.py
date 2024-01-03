from PySide2.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox
from PySide2.QtGui import QIcon
from UI_Chat import ChatWindow

class LoginWindow(QWidget):
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.initUI()

    def initUI(self):
        self.resize(350,200)
        self.setWindowTitle('SecurityChat - 登录')
        self.setWindowIcon(QIcon('img/app_icon.png'))
        self.layout = QVBoxLayout(self)

        # Username input
        self.username_label = QLabel('用户名')
        self.username_input = QLineEdit(self)
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)

        # Password input
        self.password_label = QLabel('密码')
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.password_input.returnPressed.connect(self.login) #按回车登录

        # Login button
        self.login_button = QPushButton('登录', self)
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        # Register button
        self.register_button = QPushButton('注册', self)
        self.register_button.clicked.connect(self.open_register_window)
        self.layout.addWidget(self.register_button)



    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if self.user_manager.validate_user(username, password):
            self.chat_window = ChatWindow(username) # 必须加self. 否则窗口会被销毁
            self.chat_window.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Error', '用户名或密码错误。')

    def open_register_window(self):
        self.register_window = RegisterWindow(self.user_manager)
        self.register_window.show()
        

class RegisterWindow(QWidget):
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.initUI()

    def initUI(self):
        self.resize(200,150)
        self.setWindowTitle('SecurityChat - 注册')
        self.setWindowIcon(QIcon('img/app_icon.png'))
        self.layout = QVBoxLayout(self)

        # Username input
        self.username_label = QLabel('用户名')
        self.username_input = QLineEdit(self)
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)

        # Password input
        self.password_label = QLabel('密码')
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)

        # Confirm password input
        self.confirm_password_label = QLabel('确认密码')
        self.confirm_password_input = QLineEdit(self)
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.confirm_password_label)
        self.layout.addWidget(self.confirm_password_input)
        self.confirm_password_input.returnPressed.connect(self.register) #按回车登录
        

        # Register button
        self.register_button = QPushButton('注册', self)
        self.register_button.clicked.connect(self.register)
        self.layout.addWidget(self.register_button)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if password != confirm_password:
            QMessageBox.warning(self, 'Error', 'Passwords do not match.')
            return

        # Here we should call the user registration logic
        # For demonstration, this part is simplified
        # You need to integrate the actual user registration logic here
        success = self.user_manager.register_user(username, password)  # Simplified
        if success:
            QMessageBox.information(self, 'Success', 'Registration successful.')
            self.close()
        else:
            QMessageBox.warning(self, 'Error', 'Registration failed. User might already exist.')


