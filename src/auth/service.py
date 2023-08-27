import jwt

from typing import Optional
from uuid import uuid4

from datetime import datetime, timedelta, timezone

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, update

from . import schemas, models, exceptions, utils

from ..database import get_async_session
from .config import(
    TOKEN_SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
    )
from .dao import RefreshTokenDAO, RoleDAO, UserDAO
from .models import Refresh_token, User, Role
from .schemas import RefreshSessionUpdate, UserCreate, UserCreateDB


# Определение класса для управления операциями с пользователями в базе данных
class UserCRUD:
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Создание новой записи о пользователе в базе данных
    async def create_user(self, user: UserCreate) -> models.User:
        
         # Проверка на существующего пользователя по email и username
        user_exist = await self.get_existing_user(email=user.email, username=user.username)
        
        if user_exist:
            raise exceptions.UserAlreadyExists
        
        # Генерирование уникального ID для пользователя
        id = str(uuid4())
        
         # Хеширование пароля перед сохранением
        salt = await utils.get_random_string()
        hashed_password = await utils.hash_password(user.password, salt)
        
        # Создание экземпляра User с предоставленными данными  
        db_user = await UserDAO.add(
            self.db,
            UserCreateDB(
            **user.model_dump(),
            id = id,
            hashed_password=f"{salt}${hashed_password}"
            )
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        
        return db_user
    
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:

        user = await self.get_existing_user(username=username)       
        if not user:
            raise exceptions.InvalidCredentials
         
         
        if user and await utils.validate_password(password=password, hashed_password=user.hashed_password):    
            return user
        
    
    async def logout(self, refresh_token: str = None, acces_token: str = None) -> None:
        
        if not refresh_token and not acces_token: 
            return exceptions.InactiveUser
        
        user_id= await TokenCrud.get_refresh_token_payload(self.db, refresh_token=refresh_token)
        
        refresh_session = await RefreshTokenDAO.find_one_or_none(self.db, Refresh_token.refresh_token == refresh_token)
        if refresh_session:
                await RefreshTokenDAO.delete(self.db, user_id = refresh_session.user_id)

        
        await self.update_user_statement(user_id=user_id)
        
        refresh_session.refresh_token = None
        
        await self.db.commit()
        
    
    # Проверка наличия пользователя с заданной электронной почтой, именем пользователя или ID
    async def get_existing_user(self, email: str = None, username: str = None, user_id: str = None) -> User:
        
        if not email and not username and not user_id: 
            raise exceptions.NoUserData
        
        user = await UserDAO.find_one_or_none(self.db, or_(
            User.email == email,
            User.username == username,
            User.id == user_id))
        
        return user
    
    # Обновление статуса 'is_active' пользователя
    async def update_user_statement(self, username: str = None, user_id: str = None):
        
        if not username and not user_id:
            raise exceptions.NoUserData
        
        user = await UserDAO.find_one_or_none(self.db, or_(
            User.username == username,
            User.id == user_id))
        
        # Меняем значение поля
        new_is_active = not user.is_active
        
        update_stmt = (
            update(User)
            .where(or_(User.username == username, User.id == user_id))
            .values(is_active=new_is_active)
            .returning(User.is_active)
        )
        result = await self.db.execute(update_stmt)
        
        await self.db.commit()
        
        return {"message": new_is_active}
    
    # Обновление роли пользователя
    async def update_user_role(self, user_id: User.id, new_role_id: Role.id) -> Role:
        
        # stmt = update(User).where(User.id == user_id).values(role_id=new_role_id)
        
        new_user_role = await RoleDAO.find_one_or_none(self.db,
            Role.id == new_role_id)
        
        await UserDAO.update(self.db,
            User.id == user_id,
            obj_in={"role_id": new_role_id}
        )
        
        await self.db.commit()          
        return new_user_role
    
    # Получение списка всех пользователей с поддержкой пагинации
    async def get_all_users(self, *filter, offset: int = 0, limit: int = 100, **filter_by) -> list[User]:
        
        users = await UserDAO.find_all(self.db, *filter, offset=offset, limit=limit, **filter_by)
        
        return users or {"message": "no users found"}

    
    async def get_refresh_token_by_user_id(self, user: models.User) -> models.Refresh_token:
       
        refresh_token = await RefreshTokenDAO.find_one_or_none(self.db, Refresh_token.user_id == user.id)
        
        return refresh_token
        
    async def refresh_token(self, token: str):
        
        refresh_token_session = await RefreshTokenDAO.find_one_or_none(self.db, Refresh_token.refresh_token == token)
        

        if refresh_token_session is None:
            raise exceptions.InvalidToken
        
        if datetime.now(timezone.utc) >= refresh_token_session.created_at + timedelta(seconds=refresh_token_session.expires_at):
            
            await RefreshTokenDAO.delete(id=refresh_token_session.id)
            raise exceptions.TokenExpired
        
        user = await UserDAO.find_one_or_none(self.db, id=refresh_token_session.user_id)
        
        if user is None:
            raise exceptions.InvalidToken
        
        access_token = await TokenCrud.create_access_token(self, data = user.username)
        refresh_token = await TokenCrud.create_refresh_token(self, data = user.username)
        
        refresh_token_expires = timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))
        
        
        await RefreshTokenDAO.update(
            self.db,
            Refresh_token.id == refresh_token_session.id,
            obj_in=RefreshSessionUpdate(
                refresh_token=refresh_token,
                expires_at=refresh_token_expires.total_seconds()
            )
        )
        await self.db.commit()
        
        return access_token, refresh_token


    async def delete_user(self, email: str = None, username: str = None, user_id: str = None) -> None:
        
        if not email and not username and not user_id: 
            raise exceptions.NoUserData
        
        user = await self.get_existing_user(email=email, username=username, user_id=user_id)
        
        if not user:
            raise exceptions.UserDoesNotExist
        
        refresh_token = await RefreshTokenDAO.find_one_or_none(self.db, Refresh_token.user_id == user.id)
        
        if refresh_token:
                await RefreshTokenDAO.delete(self.db, user_id = refresh_token.user_id)
        
        await UserDAO.update(
                self.db,
                User.id == user.id,
                obj_in={'is_active': False},
            )
        
        await self.db.commit()
    

# Определение класса для управления операциями с ролями в базе данных
class RoleCRUD:
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Создание новой записи о роли в базе данных
    async def create_role(self, role: schemas.RoleBase) -> models.Role:
        
        # Проверка на существующего пользователя по email и username
        if await self.get_existing_role(
        role_name=role.name):
            raise exceptions.RoleAlreadyExists
         
        db_role = Role(
            name=role.name,
            is_active_subscription=role.is_active_subscription,
            permissions=role.permissions,
        )
        
        db_role = await RoleDAO.add(
            self.db,
            UserCreateDB(
            **role.model_dump(),
            )
        )
        
        await self.db.commit()
        
        return db_role
    
    # Проверка наличия роли с заданным именем или ID
    async def get_existing_role(self, role_name: str = None, role_id: int = None) -> bool:
        
        if not role_name and not role_id:
            raise exceptions.NoRoleData
        
        role = await RoleDAO.find_one_or_none(self.db, or_(
            Role.name == role_name,
            Role.id == role_id))
        
        return role
    
    
class TokenCrud:
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    
    # Функция для создания access токена с указанием срока действия
    async def create_access_token(self, data: str):

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
        encoded_jwt = jwt.encode(to_encode, TOKEN_SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt


    # Создание refresh токена
    async def create_refresh_token(self, data: str):

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
        encoded_jwt = jwt.encode(to_encode, TOKEN_SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt


    # Создание access и refresh токенов для пользователя
    async def create_tokens(self, user_id: str) -> schemas.Token: 
        # Создание access и refresh токенов на основе payload
        access_token = await self.create_access_token(user_id)
        refresh_token = await self.create_refresh_token(user_id)

        refresh_token_expires = timedelta(
                days=int(REFRESH_TOKEN_EXPIRE_DAYS))

        db_token = await RefreshTokenDAO.add(
                    self.db,
                    schemas.RefreshSessionCreate(
                        user_id=user_id,
                        refresh_token=refresh_token,
                        expires_at=refresh_token_expires.total_seconds()
                    )
                )
        await self.db.commit()
        await self.db.refresh(db_token)

        return access_token, refresh_token
    
    
    async def get_access_token_payload(db: AsyncSession, access_token: str):
    
        try:
            decoded_payload = jwt.decode(access_token, TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
            expiration_time = datetime.utcfromtimestamp(decoded_payload['exp'])

            username = decoded_payload['sub']

            return username, expiration_time

        except jwt.ExpiredSignatureError:
            return None, None

        except jwt.DecodeError:
            raise exceptions.InvalidToken
    

    async def get_refresh_token_payload(db: AsyncSession, refresh_token: str):

        try:
            payload = jwt.decode(refresh_token,
                             TOKEN_SECRET_KEY,
                             algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise exceptions.InvalidToken
            
            return user_id

        except jwt.ExpiredSignatureError:
            raise exceptions.TokenExpired

        except jwt.DecodeError as e:
            print(e)
            raise exceptions.InvalidToken

    
# Определение класса для управления обоми crud-классами 
class DatabaseManager:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_crud = UserCRUD(db)
        self.role_crud = RoleCRUD(db)
        self.token_crud = TokenCrud(db)

    # Применение изменений к базе данных
    async def commit(self):
        await self.db.commit()