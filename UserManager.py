import json
import os
from cryptography.hazmat.primitives import serialization
from Security import generate_key_pair, serialization_key_pair

class UserManager:
    def __init__(self):
        self.users_file = 'users.json'
        self.load_users()

    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as file:
                self.users = json.load(file)
        else:
            self.users = {}

    def save_users(self):
        with open(self.users_file, 'w') as file:
            json.dump(self.users, file)

    def register_user(self, username, password):
        if username in self.users:
            return False  # 用户已存在
        public_key, private_key =  generate_key_pair()
        # 序列化密钥对
        public_pem, private_pem = serialization_key_pair(public_key, private_key)
        self.users[username] = {
            'password': password,
            'public_key': public_pem.decode('utf-8'),
            'private_key': private_pem.decode('utf-8')
        }
        self.save_users()
        return True

    def validate_user(self, username, password):
        return username in self.users and self.users[username]['password'] == password

    def get_public_key(self, username):
        if username in self.users:
            return self.users[username]['public_key']
        return None
