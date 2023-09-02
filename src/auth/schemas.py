import re
from uuid import UUID
import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Dict, Optional

from .config import (
    MIN_USERNAME_LENGTH as user_min_len,
    MAX_USERNAME_LENGTH as user_max_len,
    MIN_PASSWORD_LENGTH as pass_min_len,
    MAX_PASSWORD_LENGTH as pass_max_len,
                    )

class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_active: bool = Field(False)
    is_verified: bool = Field(False)
    is_superuser: bool = Field(False)
    

class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str
    
        
    @field_validator("username")
    def validate_username_length(cls, value):
        if len(value) < int(user_min_len) or len(value) > int(user_max_len):
            raise ValueError("Username must be between 5 and 15 characters")
        
        return value
    
    @field_validator("password")
    def validate_password_complexity(cls, value):
        if len(value) < int(pass_min_len) or len(value) > int(pass_max_len):
            raise ValueError("Password must be between 8 and 30 characters")
        
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")
        
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_-]", value):
            raise ValueError("Password must contain at least one special character")
        
        return value
    
class UserUpdate(UserBase):
    password: Optional[str] = None
        

class User(UserBase):
    id: str
    role_id: int
    
class UserCreateDB(UserBase):
    id: str
    hashed_password: Optional[str] = None
   
    

class RoleBase(BaseModel):
    name: str = Field("user")
    is_active_subscription: bool = Field(False)
    permissions: Dict

class RoleCreate(RoleBase):
    pass

class RoleCreateDB(RoleBase):
    pass

class Role(RoleBase):
    id: int
    
class RoleUpdate(RoleBase):
    name: Optional[str] = None
    
    
    
class RefreshSessionCreate(BaseModel):
    refresh_token: str
    expires_at: int
    user_id: str

class RefreshSessionUpdate(RefreshSessionCreate):
    user_id: Optional[str] = Field(None)
    
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
