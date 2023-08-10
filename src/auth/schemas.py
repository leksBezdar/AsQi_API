import re

from pydantic import BaseModel, EmailStr, validator
from typing import Dict

class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    
    @validator("username")
    def validate_username_length(cls, value):
        if len(value) < 5 or len(value) > 15:
            raise ValueError("Username must be between 5 and 15 characters")
        
        return value
    

class UserCreate(UserBase):
    hashed_password: str
    
    @validator("hashed_password")
    def validate_password_complexity(cls, value):
        if len(value) < 8 or len(value) > 30:
            raise ValueError("Password must be between 8 and 30 characters")
        
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")
        
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_-]", value):
            raise ValueError("Password must contain at least one special character")
        
        return value
        

class User(UserBase):
    id: str
    

class RoleBase(BaseModel):
    name: str
    is_active_subscription: bool
    permissions: Dict

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: int
