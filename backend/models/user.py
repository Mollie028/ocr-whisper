from sqlalchemy import Column, Integer, String
from .base import Base 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")

# --- 以下為 Pydantic schema 驗證用 ---
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(..., example="lyh")
    password: str = Field(..., example="123456")

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        orm_mode = True
