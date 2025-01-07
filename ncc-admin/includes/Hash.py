import os

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from hashlib import sha256
from jose import JWTError, jwt
from datetime import datetime, timedelta
from config import SECRET_KEY, ALGORITHM

def ncchash(ip: str, mac: str) -> str:
    #Hashes the IP and MAC address
    combined = f";{ip};{mac};"
    return sha256(combined.encode('utf-8')).hexdigest()
    
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt