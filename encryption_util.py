from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import hashlib

# No hardcoded password
RUNTIME_MASTER_PASSWORD = None

def set_master_password(password):
    global RUNTIME_MASTER_PASSWORD
    print(f"[DEBUG] Master password set to: {password}")  # TEMP
    RUNTIME_MASTER_PASSWORD = password

def derive_key(password):
    return hashlib.sha256(password.encode()).digest()

def pad(text):
    padding_len = 16 - len(text) % 16
    return text + chr(padding_len) * padding_len

def unpad(text):
    padding_len = ord(text[-1])
    return text[:-padding_len]

def encrypt_password(raw_password):
    key = derive_key(RUNTIME_MASTER_PASSWORD)
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(raw_password).encode('utf-8'))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv + ":" + ct

def decrypt_password(enc_password):
    try:
        key = derive_key(RUNTIME_MASTER_PASSWORD)
        iv, ct = enc_password.split(":")
        iv = base64.b64decode(iv)
        ct = base64.b64decode(ct)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = cipher.decrypt(ct).decode('utf-8')
        return unpad(pt)
    except Exception as e:
        return "[Decryption Failed]"