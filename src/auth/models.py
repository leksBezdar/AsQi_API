from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, JSON
from ..database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    user_set_id = Column(String, nullable=True, unique=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), default=1)
    refresh_token = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    is_superuser = Column(Boolean, nullable=False, default=False)
    is_verified = Column(Boolean, nullable=False, default=False)

    role = relationship("Role", back_populates="users")

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    is_active_subscription = Column(Boolean, nullable=False, default=False)
    permissions = Column(JSON, nullable=False, default={})

    users = relationship("User", back_populates="role")
