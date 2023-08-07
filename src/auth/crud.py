import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, update

from .models import User, Role
from . import schemas


async def create_user(db: AsyncSession, user: schemas.UserBase):
    db_user = User(
        email=user.email, 
        username=user.username,              
        hashed_password=user.hashed_password, 
        is_active=user.is_active,                
        is_superuser=user.is_superuser, 
        is_verified=user.is_verified,
        role_id=user.role_id,
    )  
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


async def get_user_by_email(db: AsyncSession, user_email: str):
    
    """ Возвращает информацию о пользователе по email """
    
    stmt = select(User).where(User.email == user_email)
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
     
    return user



async def get_user_by_username(db: AsyncSession, username: str):
    
    """ Возвращает информацию о пользователе по имени """
    
    stmt = select(User).where(User.username == username)
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    return user



async def get_existing_user(db: AsyncSession, email: str, username: str):
    
    """ Проверка на существующего пользователя """
    
    email_exists = await get_user_by_email(db, email)
    username_exists = await get_user_by_username(db, username)
    
    return email_exists or username_exists


async def create_role(db: AsyncSession, role: schemas.RoleBase):
    db_role = Role(
        name=role.name,
        is_active_subscription=role.is_active_subscription,
        permissions=role.permissions,
    )
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    
    return db_role


async def check_existing_role(db: AsyncSession, role_name: str):
    
    """ Возвращает информацию о существующей роли пользователе """
    
    query = select(Role).where(Role.name == role_name)
    
    result = await db.execute(query)
    role = result.scalar_one_or_none()
    
    return role


async def get_role_by_id(db: AsyncSession, role_id: int):
    
    """ Возвращает информацию о пользователе по айди"""
    
    query = select(Role.name).where(Role.id == role_id)
    
    result = await db.execute(query)
    role_name = result.scalar_one_or_none()
    
    return role_name


async def update_user_role(db: AsyncSession, user_id: int, new_role_id: int):
    
    """ Меняет роль пользователя """
    
    stmt = update(User).where(User.id == user_id).values(role_id=new_role_id)
    await db.execute(stmt)
      
    query = select(Role).where(Role.id == new_role_id)

    result = await db.execute(query)
    new_user_data = result.scalar_one_or_none()
    
    return new_user_data


async def read_all_users(db: AsyncSession, skip: int = 0, limit: int = 10):
    query = select(User).offset(skip).limit(limit)
    
    result = await db.execute(query)
    
    return result.scalars().all()


def get_random_string(length=12):
    
    """ Генерирует случайную строку, использующуюся как соль """
    
    return "".join(random.choice(string.ascii_letters) for _ in range(length))
    
    

    