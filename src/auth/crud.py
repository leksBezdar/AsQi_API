import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, update


from .models import User, Role
from . import schemas, models, exceptions, auth


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    
    id = auth.get_random_string(random.randint(8, 12))
    
    db_user = User(
        id=id,
        email=user.email, 
        username=user.username,              
        hashed_password=user.hashed_password, 
        is_active=user.is_active,                
        is_superuser=user.is_superuser, 
        is_verified=user.is_verified,
    )  
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


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


async def get_user_by_id(db: AsyncSession, user_id: str):
    
    """ Возвращает информацию о пользователе по имени """
    
    stmt = select(User).where(User.id == user_id)
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    return user


async def get_existing_user(db: AsyncSession, email: str = None , username: str = None, user_id: str = None):
    
    """ Проверка на существующего пользователя """
    
    if email is None and username is None and user_id == None:
        raise exceptions.NoData()
    
    email_exists = await get_user_by_email(db, email)
    username_exists = await get_user_by_username(db, username)
    id_exists = await get_user_by_id(db, user_id)
    
    return email_exists or username_exists or id_exists



async def get_role_by_name(db: AsyncSession, role_name: int):
    
    """ Возвращает информацию о роли по имени """
    
    stmt = select(Role).where(Role.name == role_name)
    
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    
    return role


async def get_role_by_id(db: AsyncSession, role_id: int):
    
    """ Возвращает информацию о роли по айди"""
    
    query = select(Role).where(Role.id == role_id)
    
    result = await db.execute(query)
    role = result.scalar_one_or_none()
    
    print(bool(role))
    
    return role



async def get_existing_role(db: AsyncSession, role_name: str = None, role_id: int = -1):
    
    """ Возвращает информацию о существующей роли пользователе """
    
    if role_name is None and role_id == -1:
        raise exceptions.NoData()
    
    role_id_exists = await get_role_by_id(db, role_id)
    role_name_exists = await get_role_by_name(db, role_name)
    
    return role_id_exists or role_name_exists




async def read_all_users(db: AsyncSession, skip: int = 0, limit: int = 10):
    query = select(User).offset(skip).limit(limit)
    
    result = await db.execute(query)
    
    return result.scalars().all()


async def patch_refresh_token(db: AsyncSession, user: models.User, new_refresh_token: str):
    user.refresh_token = new_refresh_token
    await db.commit()
    return user


async def update_user_role(db: AsyncSession, user_id: str, new_role_id: int):
    
    """ Меняет роль пользователя """
    
    stmt = update(User).where(User.id == user_id).values(role_id=new_role_id)
    await db.execute(stmt)
      
    query = select(Role).where(Role.id == new_role_id)

    result = await db.execute(query)
    new_user_data = result.scalar_one_or_none()
    
    return new_user_data
    
    

    