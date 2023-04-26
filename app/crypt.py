# System imports
import hashlib
# Libs imports
from cryptography.fernet import Fernet

f = Fernet(b'7Uzv2ECpEFXcYUU-7nJWA5n9LptOTa1w9lMNdlkQOUM=')

def encrypt(text: str):
    return f.encrypt(text.encode())

def decrypt(text: str):
    return f.decrypt(text).decode()

def hash_password(password: str):
    return hashlib.sha256(f'{password}'.encode('utf-8')).hexdigest()
