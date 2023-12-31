import sqlalchemy as sa

from datetime import datetime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Integer, Boolean, ForeignKey, JSON, String

from ..database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    user_set_id: Mapped[str] = mapped_column(nullable=True, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    role: Mapped[relationship] = relationship("Role", back_populates="users")


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    is_active_subscription: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    permissions: Mapped[dict] = mapped_column(JSON, nullable=False, default={})

    users: Mapped[relationship] = relationship("User", back_populates="role")
    
    
class Refresh_token(Base):
    __tablename__ = 'refresh_tokens'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    refresh_token: Mapped[str] = sa.Column(String, index=True)
    expires_at: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(sa.TIMESTAMP(timezone=True),
                                                 server_default=func.now())
    user_id: Mapped[str] = mapped_column(String, sa.ForeignKey(
        "users.id", ondelete="CASCADE"))
