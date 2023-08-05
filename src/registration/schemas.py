from pydantic import BaseModel
from typing import Dict


class UserBase(BaseModel):
    role_id: int
    email: str
    username: str
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    

class User(UserBase):
    id: int
    
    

class RoleBase(BaseModel):
    name: str
    is_active_subscription: bool
    permissions: Dict
    
    
class Role(RoleBase):
    id: int
