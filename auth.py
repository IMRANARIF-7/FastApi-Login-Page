from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt 
import secrets
import os
from dotenv import load_dotenv 

load_dotenv()  

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password:str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

Secret_Key = os.getenv("SECRET_KEY")
Algorithm = os.getenv("ALGORITHM", "HS256")
Token_expire = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if not Secret_Key:
    raise ValueError("SECRET_KEY must be set in .env")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=Token_expire))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Secret_Key, algorithm=Algorithm)
    return encoded_jwt

def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)