from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

# 生成密钥对
def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    
    return public_key, private_key

def serialization_key_pair(public_key, private_key):
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return public_pem, private_pem

def deserialization_key_pair(public_pem, private_pem):
    public_key = serialization.load_pem_public_key(
        public_pem,
        backend=default_backend()
    ) if public_pem is not None else None
    private_key = serialization.load_pem_private_key(
        private_pem,
        password=None,  # 如果私钥被密码保护，则需要提供密码
        backend=default_backend()
    ) if private_pem is not None else None
    return public_key, private_key

# 加密消息
def encrypt_message(message, public_key):
    encrypted_message = public_key.encrypt(
        message.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # print(type(encrypted_message))
    return encrypted_message

# 解密消息
def decrypt_message(encrypted_message, private_key):
    decrypted_message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_message.decode('utf-8')

# 生成数字签名
def generate_signature(message, private_key):
    if isinstance(message, str):
        message = message.encode('utf-8')
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

# 验证数字签名
def verify_signature(message, signature, public_key):
    if isinstance(message, str):
        message = message.encode('utf-8')
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False

# 测试代码
def main():
    # 生成密钥对
    public_key, private_key = generate_key_pair()

    # 要发送的消息
    message = "Hello, Bob!"

    # 使用私钥生成数字签名
    signature = generate_signature(message, private_key)
    print("Signature:", signature)

    # 使用公钥加密消息
    encrypted_message = encrypt_message(message, public_key)
    print("Encrypted Message:", encrypted_message)
    print(type(encrypted_message))

    # 使用私钥解密消息
    decrypted_message = decrypt_message(encrypted_message, private_key)
    print("Decrypted Message:", decrypted_message)

    # 使用公钥验证数字签名
    is_valid_signature = verify_signature(decrypted_message, signature, public_key)
    print("Is Valid Signature:", is_valid_signature)

    # 使用公钥加密伪造消息
    fake_encrypted_message = encrypt_message("fuck bob", public_key)
    print("Encrypted Message:", fake_encrypted_message)

    # 使用私钥解密伪造消息
    fake_decrypted_message = decrypt_message(fake_encrypted_message, private_key)
    print("Decrypted Message:", fake_decrypted_message)

    # 使用公钥验证数字签名
    is_valid_signature = verify_signature(fake_decrypted_message, signature, public_key)
    print("Is Valid Signature:", is_valid_signature)

if __name__ == '__main__':
    main()