from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.core.db import Base
from datetime import datetime
from typing import Optional

# --- 使用者資料表 ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)
    role = Column(String, default="user")
    can_view_all = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# --- 名片資料表（Card）---
class Card(Base):
    __tablename__ = "business_cards"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=True)
    raw_text = Column(String, nullable=True)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    title = Column(String, nullable=True)
    company_name = Column(String, nullable=True)

# --- 以下為 Pydantic schema ---
from pydantic import BaseModel, Field
from typing import Optional

# 註冊使用者用
class UserCreate(BaseModel):
    username: str = Field(..., example="lyh")
    password: str = Field(..., example="123456")
    company_name: Optional[str] = None

# 登入用
class UserLogin(BaseModel):
    username: str
    password: str

# 查詢使用者資訊用
class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool

    class Config:
        orm_mode = True
