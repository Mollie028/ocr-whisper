from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.db import get_db
from services import user_service
from core import security

router = APIRouter()

# ---------- 請求模型 ----------
class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str

class LoginRequest(BaseModel):
    username: str
    password: str

# ---------- 註冊 ----------
@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = user_service.get_user_by_username(db, request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="帳號已存在"
        )
    user = user_service.create_user(db, request.username, request.password, request.role)
    return {"message": "註冊成功", "username": user.username, "role": user.role}

# ---------- 登入 ----------
@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤"
        )
    token = security.create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role}
