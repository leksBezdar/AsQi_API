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


async def get_existing_email(db: AsyncSession, user_email: str):
    stmt = select(User).where(User.email == user_email)
    
    result = await db.execute(stmt)
    is_exist = bool(result.scalar_one_or_none())
    
    return is_exist



async def get_existing_username(db: AsyncSession, username: str):
    stmt = select(User).where(User.username == username)
    
    result = await db.execute(stmt)
    is_exist = bool(result.scalar_one_or_none())
    
    return is_exist


async def get_existing_user(db: AsyncSession, email: str, username: str):
    email_exists = await get_existing_email(db, email)
    username_exists = await get_existing_username(db, username)
    
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
    stmt = select(Role).where(Role.name == role_name)
    
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    
    return role


async def get_role_by_id(db: AsyncSession, role_id: int):
    stmt = select(Role.name).where(Role.id == role_id)
    
    result = await db.execute(stmt)
    role_name = result.scalar_one_or_none()
    
    return role_name


async def update_user_role(db: AsyncSession, user_id: int, new_role_id: int):
    query = update(User).where(User.id == user_id).values(role_id=new_role_id)
    await db.execute(query)
      
    stmt = select(Role).where(Role.id == new_role_id)

    result = await db.execute(stmt)
    new_user_data = result.scalar_one_or_none()
    
    return new_user_data


async def read_all_users(db: AsyncSession, skip: int = 0, limit: int = 10):
    stmt = select(User).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    
    return result.scalars().all()
    
    
    
    
    
    
    