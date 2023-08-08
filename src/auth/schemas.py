from pydantic import BaseModel
from typing import Dict

class UserBase(BaseModel):
    email: str
    username: str
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    refresh_token:str
    

class RoleBase(BaseModel):
    name: str
    is_active_subscription: bool
    permissions: Dict

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: int
