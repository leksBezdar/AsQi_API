import hashlib
import random
import string
import jwt

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta

from .models import User
from . import crud
from ..database import AsyncSession
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta = None):
    
    """ Создает access токен """
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def create_refresh_token(data: dict):
    
    """ Создает refresh токен """
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt



def create_tokens(user: User): 
    payload = {
        "sub": user.username
    }
    
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    
    return access_token, refresh_token


def get_random_string(length=12):
    
    """ Генерирует случайную строку, использующуюся как соль """
    
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def validate_password(password: str, hashed_password: str):
    
    """ Проверяет, что хеш пароля совпадает c хешем из БД """
    
    salt, hashed = hashed_password.split("$")
    
    return hash_password(password, salt) == hashed


def hash_password(password: str, salt: str = None):
    
    """ Хеширует пароль c солью """
    
    if salt is None:
        salt = crud.get_random_string()
        
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)

    return enc.hex()
