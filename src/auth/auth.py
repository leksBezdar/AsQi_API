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
from .config import(
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
    )


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Функция для создания access токена с указанием срока действия
def create_access_token(data: dict, expires_delta: timedelta = None):
    
    """ Создает access токен """
    
    # Создание словаря с данными для кодирования
    to_encode = data.copy()
    
    # Вычисление времени истечения срока действия токена
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    # Кодирование токена с использованием секретного ключа и алгоритма
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt



# Создание refresh токена
def create_refresh_token(data: dict):
    
    """ Создает refresh токен """
    
    # Копирование данных для кодирования
    to_encode = data.copy()
    
    # Вычисление даты истечения срока действия
    expire = datetime.utcnow() + timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))
    
    # Добавление информации о сроке действия в данные и кодирование токена
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


# Создание access и refresh токенов для пользователя
def create_tokens(user: User): 
    payload = {
        "sub": user.username
    }
    
    # Создание access и refresh токенов на основе payload
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    
    return access_token, refresh_token


# Генерация случайной строки заданной длины
def get_random_string(length=16):
    
    """ Генерирует случайную строку, использующуюся как соль """
    
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


# Генерация случайного идентификатора заданной длины
def get_random_user_id(email: str):
    
    # Генерируем случайную строку в качестве соли
    salt = get_random_string()
    
    # Комбинируем email и соль
    combined_data = f"{email}{salt}"
    
    # Создаем хеш с использованием SHA-256
    hashed_id = hashlib.sha256(combined_data.encode()).hexdigest()
    
    return hashed_id


# Проверка пароля на соответствие хешированному паролю
def validate_password(password: str, hashed_password: str):
    
    """ Проверяет, что хеш пароля совпадает c хешем из БД """
    
    # Разделение хеша пароля на соль и хешированную часть
    salt, hashed = hashed_password.split("$")
    
    # Сравнение хешированного пароля
    return hash_password(password, salt) == hashed


# Метод для хеширования пароля с учетом соли
def hash_password(password: str, salt: str = None):
    
    """ Хеширует пароль c солью """
    
    # Если соль не указана, генерируем случайную соль
    if salt is None:
        salt = crud.get_random_string()
        
    # Применение хэш-функции PBKDF2 к паролю и соли
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)

    return enc.hex()
