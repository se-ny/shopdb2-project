from sqlalchemy import Column, BigInteger, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_code = Column(String(30), unique=True, nullable=False)
    role_name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(BigInteger, ForeignKey("users.user_id"), primary_key=True)
    role_id = Column(BigInteger, ForeignKey("roles.role_id"), primary_key=True)
    assigned_at = Column(DateTime, server_default=func.now())


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    org_id = Column(BigInteger, ForeignKey("org_units.org_id"), nullable=True)
    login_id = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(30), nullable=True)
    user_status = Column(
        Enum("ACTIVE", "INACTIVE", "SUSPENDED", "WITHDRAWN", name="user_status_enum"),
        default="ACTIVE",
    )
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # user_roles를 거쳐 Role 객체를 바로 리스트로 가져옴 (읽기 전용)
    roles = relationship("Role", secondary="user_roles", viewonly=True)