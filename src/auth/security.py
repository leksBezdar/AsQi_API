import hashlib
import random
import string
from fastapi import Depends
import jwt

from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from datetime import datetime, timedelta

from .dao import RefreshTokenDAO


from .models import User
from . import exceptions, schemas
from ..database import AsyncSession, get_async_session
from .config import(
    REFRESH_TOKEN_SECRET_KEY,
    ACCESS_TOKEN_SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
    )

from .crud import DatabaseManager


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Функция для создания access токена с указанием срока действия
# Функция для создания access токена с указанием срока действия
async def create_access_token(data: str):
    
    """ Создает access токен """
    
    data_dict = {
        "sub": data
    }
    
    # Создание словаря с данными для кодирования
    to_encode = data_dict.copy()
    
    # Вычисление времени истечения срока действия токена
    expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    # Кодирование токена с использованием секретного ключа и алгоритма
    encoded_jwt = jwt.encode(to_encode, ACCESS_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


# Создание refresh токена
# Создание refresh токена
async def create_refresh_token(data: str):
    
    """ Создает refresh токен """
    
    data_dict = {
        "sub": data
    }
    
    # Копирование данных для кодирования
    to_encode = data_dict.copy()
    
    # Вычисление даты истечения срока действия
    expire = datetime.utcnow() + timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))
    
    # Добавление информации о сроке действия в данные и кодирование токена
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


# Создание access и refresh токенов для пользователя
async def create_tokens(db: AsyncSession, user_id: str) -> schemas.Token: 
    # Создание access и refresh токенов на основе payload
    access_token = await create_access_token(user_id)
    refresh_token = await create_refresh_token(user_id)
    
    refresh_token_expires = timedelta(
            days=int(REFRESH_TOKEN_EXPIRE_DAYS))
    
    db_token = await RefreshTokenDAO.add(
                db,
                schemas.RefreshSessionCreate(
                    user_id=user_id,
                    refresh_token=refresh_token,
                    expires_at=refresh_token_expires.total_seconds()
                )
            )
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)
    
    return access_token, refresh_token
    


# Генерация случайной строки заданной длины
async def get_random_string(length=16):
    
    """ Генерирует случайную строку, использующуюся как соль """
    
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


async def get_current_user(db: AsyncSession, refresh_token: str):
    
    db_manager = DatabaseManager(db)
    user_crud = db_manager.user_crud
    
    user = await user_crud.get_user_by_token(db, refresh_token)
    
    if not user:
        raise exceptions.InvalidAuthenthicationCredential
        
    if not user.is_active:
        raise exceptions.InactiveUser
        
    return user


async def get_access_token_payload(access_token: str, db: AsyncSession = Depends(get_async_session)):
    
    try:
        decoded_payload = jwt.decode(access_token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        expiration_time = datetime.utcfromtimestamp(decoded_payload['exp'])

        username = decoded_payload['sub']

        return username, expiration_time

    except jwt.ExpiredSignatureError:
        return None, None
    
    except jwt.DecodeError:
        raise exceptions.InvalidToken
    

async def get_refresh_token_payload(refresh_token: str):
    
    try:
        decoded_payload = jwt.decode(refresh_token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        expiration_time = datetime.utcfromtimestamp(decoded_payload['exp'])
        username = decoded_payload['sub']
        
        return username, expiration_time
    
    except jwt.ExpiredSignatureError:
        raise exceptions.TokenExpired
    
    except jwt.DecodeError:
        raise exceptions.InvalidToken
    

# Проверка пароля на соответствие хешированному паролю
async def validate_password(password: str, hashed_password: str):
    
    """ Проверяет, что хеш пароля совпадает c хешем из БД """
    
    # Разделение хеша пароля на соль и хешированную часть
    salt, hashed = hashed_password.split("$")
    
    # Сравнение хешированного пароля
    return await hash_password(password, salt) == hashed


# Метод для хеширования пароля с учетом соли
async def hash_password(password: str, salt: str = None):
    
    """ Хеширует пароль c солью """
    
    # Если соль не указана, генерируем случайную соль
    if salt is None:
        salt = await get_random_string()
        
    # Применение хэш-функции PBKDF2 к паролю и соли
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)

    return enc.hex()


async def update_user_tokens(refresh_token: str, db: AsyncSession):
    try:  
        username, expiration_time = await get_refresh_token_payload(refresh_token)
        
        if username is None or expiration_time is None:
            raise exceptions.InvalidToken
        
        db_manager = DatabaseManager(db)
        user_crud = db_manager.user_crud
        
        user = await user_crud.get_user_by_username(username)
        
        if user is None or user.refresh_token != refresh_token:
            raise exceptions.InvalidToken
        
        new_access_token, new_refresh_token = await create_tokens(user)
        
        
        await user_crud.patch_refresh_token(user=user, new_refresh_token=new_refresh_token)
        
        response_content = {
            "message": "Tokens refreshed successfully",
        }
        
        response = JSONResponse(content=response_content)
        
        response.set_cookie(key="access_token", value=new_access_token, httponly=True)
        response.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True)
        
        return response
    
    except jwt.ExpiredSignatureError:
        raise exceptions.TokenExpired
        
    except jwt.DecodeError:
        raise exceptions.InvalidToken