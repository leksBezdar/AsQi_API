import hashlib
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta


from .import crud
from ..database import AsyncSession
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


# Загружаем секретный ключ, который будет использоваться для подписи токенов
SECRET_KEY = SECRET_KEY
ALGORITHM = ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES

# OAuth2PasswordBearer позволяет извлекать токен из заголовков запроса
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_password(password: str, hashed_password: str):
    
    """ Проверяет, что хеш пароля совпадает c хешем из БД """
    
    salt, hashed = hashed_password.split("$")
    print(salt, hashed)
    
    return hash_password(password, salt) == hashed


def hash_password(password: str, salt: str = None):
    
    """ Хеширует пароль c солью """
    
    if salt is None:
        salt = crud.get_random_string()
        print(salt)
        
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    print(enc.hex())

    return enc.hex()

def create_access_token(data: dict, expires_delta: timedelta = None):
    
    """ Создает access токен """
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.DecodeError:
        raise credentials_exception

    db = AsyncSession()
    user = crud.get_user_by_username(db, username)
    
    if user is None:
        raise credentials_exception
    return user


