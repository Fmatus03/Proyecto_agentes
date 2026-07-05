from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    rol = Column(String(255), nullable=True)
    estado = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class Roles(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=True)
    descripcion = Column(String(255), nullable=True)
    estado = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class Permissions(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True)
    codigo = Column(String(255), nullable=True)
    descripcion = Column(String(255), nullable=True)
    modulo = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class RolePermissions(Base):
    __tablename__ = 'role_permissions'
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer(), nullable=True)
    permission_id = Column(Integer(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class AuditLogs(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer(), nullable=True)
    action = Column(String(255), nullable=True)
    entity = Column(String(255), nullable=True)
    entity_id = Column(Integer(), nullable=True)
    detail = Column(String(255), nullable=True)
    ip_address = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=True)
    value = Column(String(255), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

class PasswordResetTokens(Base):
    __tablename__ = 'password_reset_tokens'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer(), nullable=True)
    token_hash = Column(String(255), nullable=True)
    expires_at = Column(DateTime(), nullable=True)
    used_at = Column(DateTime(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)
