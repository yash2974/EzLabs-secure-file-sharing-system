from passlib.context import CryptContext
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
FERNET_SECRET = os.getenv("FERNET_SECRET")
if not FERNET_SECRET:
    raise ValueError("FERNET_SECRET not set in environment!")

fernet = Fernet(FERNET_SECRET.encode())

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def generate_verification_token(email: str) -> str:
    return fernet.encrypt(email.encode()).decode()

def decrypt_verification_token(token: str, ttl_seconds: int = 600000) -> str:
    return fernet.decrypt(token.encode(), ttl=ttl_seconds).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def encrypted_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()
