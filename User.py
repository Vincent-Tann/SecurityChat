from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import json

# 用户类
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def serialize_keys(self):
        # 序列化公钥和私钥
        private_key = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_key = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return private_key, public_key

# 用户注册
def register_user(username, password):
    user = User(username, password)
    private_key, public_key = user.serialize_keys()
    # 存储用户信息和密钥（此处简化为存储到文件，实际项目中应使用数据库）
    with open(f'{username}_keys.json', 'w') as f:
        json.dump({
            'private_key': private_key.decode('utf-8'),
            'public_key': public_key.decode('utf-8')
        }, f)
    return user

# 消息加密
def encrypt_message(message, public_key):
    encrypted = public_key.encrypt(
        message.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted

# 示例注册和加密消息
user = register_user("alice", "password123")
encrypted_message = encrypt_message("Hello, Bob!", user.public_key)
print(encrypted_message)
