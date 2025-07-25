from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.core.db import Base
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# --- 使用者資料表 ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    company_name = Column(String)
    role = Column(String)  # admin / user
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# --- 名片資料表（Card）---
class Card(Base):
    __tablename__ = "business_cards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    title = Column(String, nullable=True)
    company_name = Column(String, nullable=True)

# --- 以下為 Pydantic schema ---

# 註冊使用者用
class UserCreate(BaseModel):
    username: str
    password: str
    company_name: Optional[str] = None
    is_admin: Optional[bool] = False

# 登入用
class UserLogin(BaseModel):
    username: str
    password: str

# 查詢使用者資訊用
class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    company_name: str
    is_active: bool
    role: Optional[str] = None       # ✅ 允許為 None
    note: Optional[str] = None

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    note: str = ""
    is_admin: bool = False
    is_active: bool = True


