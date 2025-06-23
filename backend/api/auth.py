# backend/api/auth.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from psycopg2.extras import RealDictCursor
import psycopg2
from backend.core.db import get_conn
from backend.core.security import hash_password, verify_password, create_jwt_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# --------------------
# 輸入模型
# --------------------
class RegisterInput(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginInput(BaseModel):
    email: EmailStr
    password: str

# --------------------
# 註冊 API
# --------------------
@router.post("/register")
def register(data: RegisterInput):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # 檢查帳號是否存在
    cur.execute("SELECT * FROM users WHERE email = %s", (data.email,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="該信箱已註冊")

    hashed = hash_password(data.password)
    cur.execute(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
        (data.username, data.email, hashed)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"msg": "✅ 註冊成功"}

# --------------------
# 登入 API
# --------------------
@router.post("/login")
def login(data: LoginInput):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM users WHERE email = %s", (data.email,))
    user = cur.fetchone()

    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="❌ 帳號或密碼錯誤")

    token = create_jwt_token(user_id=user["id"], role=user.get("role", "user"))

    cur.close()
    conn.close()

    return {"access_token": token, "user": {"id": user["id"], "username": user["username"], "role": user["role"]}}
