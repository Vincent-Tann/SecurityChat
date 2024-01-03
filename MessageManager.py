import json
import os
import base64
from UserManager import UserManager
from Security import deserialization_key_pair, decrypt_message

class MessageManager:
    def __init__(self):
        self.messages_file = 'messages.json'
        self.load_messages()

    def load_messages(self):
        if os.path.exists(self.messages_file):
            with open(self.messages_file, 'r') as file:
                self.messages = json.load(file)
        else:
            self.messages = []

    def save_messages(self):
        with open(self.messages_file, 'w') as file:
            json.dump(self.messages, file)

    def add_message(self, sender, receiver, timestamp, encrypted_message, plain_message, signature):
        self.messages.append({
            'sender': sender,
            'receiver': receiver,
            'timestamp': timestamp,
            # 'encrypted_message': encrypted_message.decode('utf-8'),
            'encrypted_message': base64.b64encode(encrypted_message).decode('utf-8'),
            'plain_message': plain_message,
            'signature': base64.b64encode(signature).decode('utf-8')
        })
        self.save_messages()

    def get_messages_for_user(self, username):
        return [msg for msg in self.messages if msg['receiver'] == username or msg['sender'] == username]
    
    def get_messages_between_users(self, user1, user2):
        """
        获取两个用户之间的消息记录
        :param user1: 用户1的用户名
        :param user2: 用户2的用户名
        :return: 两个用户之间的消息列表
        """
        filtered_messages = []
        for msg in self.messages:
            if (msg['sender'] == user1 and msg['receiver'] == user2) or \
               (msg['sender'] == user2 and msg['receiver'] == user1):
                filtered_messages.append(msg)
        # 按timestamp字段进行排序
        return sorted(filtered_messages, key=lambda x: x['timestamp'])
    
    def get_plain_message(self, message, user):
        # 给定消息库中取出的一条message和读消息的人user，用安全方式读取消息
        sender = message['sender']
        receiver = message['receiver']
        user_manager = UserManager()

        if user == receiver:
            private_pem = user_manager.users[user]['private_key'].encode('utf-8')
            _, private_key = deserialization_key_pair(None, private_pem)
            encrypted_message = message['encrypted_message']
            plain_message = decrypt_message(base64.b64decode(encrypted_message), private_key)

        elif user == sender:
            plain_message = message['plain_message']
        
        else:
            print(f"Not message from/to {user}!")
            plain_message = ""
        
        return plain_message