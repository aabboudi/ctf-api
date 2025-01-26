from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from hashlib import sha256
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.db.config import SECRET_KEY, ALGORITHM

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend

# Key Hashing Context
hsah_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token generation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_ncchash(ip: str, mac: str) -> str:
  # Hash the IP and MAC addresses
  combined = f";{ip};{mac};"
  return sha256(combined.encode('utf-8')).hexdigest()
    
def create_access_token(data: dict, expires_delta: timedelta | None = None):
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.now() + expires_delta
  else:
    expire = datetime.now() + timedelta(minutes=15)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt

def encrypt_flag(ncchash: str, flag: str) -> dict:
  try:
    key = bytes.fromhex(ncchash)[:32]
    iv = bytes.fromhex(ncchash)[:-17:-1]
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(flag.encode('utf-8')) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return ciphertext.hex()
  except ValueError as e:
    raise ValueError(f"Invalid input: {e}")
  except Exception as e:
    raise Exception(f"Encryption failed: {str(e)}")

def decrypt_flag(ncchash: str, ciphertext: str) -> str:
  try:
    key = bytes.fromhex(ncchash)[:32]
    iv = bytes.fromhex(ncchash)[:-17:-1]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(bytes.fromhex(ciphertext)) + decryptor.finalize()
    unpadder = PKCS7(algorithms.AES.block_size).unpadder()
    flag = unpadder.update(padded_data) + unpadder.finalize()
    return flag.decode('utf-8')
  except ValueError as e:
    raise ValueError(f"Invalid input: {e}")
  except Exception as e:
    raise Exception(f"Decryption failed: {str(e)}")
