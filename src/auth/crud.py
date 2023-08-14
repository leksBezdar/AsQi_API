from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, update
from uuid import uuid4

from .models import User, Role
from . import schemas, models, exceptions

class UserCRUD:
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user: schemas.UserBase):
        id = str(uuid4())
        db_user = User(
            id=id,
            email=user.email, 
            username=user.username,              
            hashed_password=user.hashed_password, 
            is_active=False,       
            is_superuser=False,
            is_verified=False,
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
    
    async def get_user_by_email(self, user_email: str):
        stmt = select(User).where(User.email == user_email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        return user
    
    async def get_user_by_username(self, username: str):
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        return user
    
    async def get_user_by_id(self, user_id: str):
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        return user
    
    async def get_user_by_token(self, refresh_token: str):
        if not refresh_token: 
            raise exceptions.TokenWasNotFount
        query = select(User).where(User.refresh_token == refresh_token)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        return user
    
    async def get_user_role_id(self, username: str = None, user_id: str = None, user_email: str = None):
        user_role_id = select(User.role_id).where(User.username == username)
        result = await self.db.execute(user_role_id)
        role_id = result.scalar_one_or_none()
        return role_id
    
    async def get_existing_user(self, email: str = None, username: str = None, user_id: str = None):
        if email is None and username is None and user_id == None:
            raise exceptions.NoData()
        email_exists = await self.get_user_by_email(email)
        username_exists = await self.get_user_by_username(username)
        id_exists = await self.get_user_by_id(user_id)
        return email_exists or username_exists or id_exists
    
    async def update_user_statement(self, username: str = None, user_id: str = None):
        if not username and not user_id:
            raise exceptions.NoUserData
        
        query = select(User.is_active).where(or_(User.username == username, User.id == user_id))
        result = await self.db.execute(query)
        is_active_stmt = result.fetchone()
        
        new_is_active = not is_active_stmt[0]
        
        update_stmt = (
            update(User)
            .where(or_(User.username == username, User.id == user_id))
            .values(is_active=new_is_active)
            .returning(User.is_active)
        )
        result = await self.db.execute(update_stmt)
        await self.db.commit()
        
        return {"message": new_is_active}
    
    async def update_user_role(self, user_id: str, new_role_id: int):
        stmt = update(User).where(User.id == user_id).values(role_id=new_role_id)
        await self.db.execute(stmt)
        await self.db.commit()
        
        query = select(Role).where(Role.id == new_role_id)
        result = await self.db.execute(query)
        new_user_data = result.scalar_one_or_none()
        
        return new_user_data
    
    async def get_all_users(self, skip: int = 0, limit: int = 10):
        query = select(User).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def patch_refresh_token(self, user: models.User, new_refresh_token: str):
        user.refresh_token = new_refresh_token
        await self.db.commit()
        return user

    


class RoleCRUD:
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_role(self, role: schemas.RoleBase):
        db_role = Role(
            name=role.name,
            is_active_subscription=role.is_active_subscription,
            permissions=role.permissions,
        )
        self.db.add(db_role)
        await self.db.commit()
        await self.db.refresh(db_role)
        return db_role
    
    async def get_role_by_name(self, role_name: str):
        query = select(Role).where(Role.name == role_name)
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        return role
    
    async def get_role_by_id(self, role_id: int):
        query = select(Role.name).where(Role.id == role_id)
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        return role
    
    async def get_existing_role(self, role_name: str = None, role_id: int = None):
        if not role_name and not role_id:
            raise exceptions.NoRoleData()
        
        role_id_exists = await self.get_role_by_id(role_id)
        role_name_exists = await self.get_role_by_name(role_name)
        
        return role_id_exists or role_name_exists

    

class DatabaseManager:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_crud = UserCRUD(db)
        self.role_crud = RoleCRUD(db)

    async def commit(self):
        await self.db.commit()