from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
from backend.core.db import get_conn
from backend.core.security import hash_password, verify_password, create_jwt_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# --------------------
# 輸入模型
# --------------------
class RegisterInput(BaseModel):
    username: str
    password: str
    is_admin: bool = False
    can_view_all: bool = False
    company_name: str = ""  # 可選填

class LoginInput(BaseModel):
    username: str
    password: str

# --------------------
# 註冊 API
# --------------------
@router.post("/register")
def register(data: RegisterInput):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM users WHERE username = %s", (data.username,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="此帳號已存在，請換一個")

    hashed = hash_password(data.password)
    is_admin = data.role == "admin"
    can_view_all = is_admin

    print("✅ 準備寫入：", data.username)

    cur.execute(
        """
        INSERT INTO users (username, password_hash, is_admin, can_view_all)
        VALUES (%s, %s, %s, %s)
        """,
        (data.username, hashed, is_admin, can_view_all)
    )

    conn.commit()
    print("✅ commit 完成")

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

    cur.execute("SELECT * FROM users WHERE username = %s", (data.username,))
    user = cur.fetchone()

    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="❌ 帳號或密碼錯誤")

    token = create_jwt_token(
        user_id=user["id"],
        role="admin" if user["is_admin"] else "user"
    )

    cur.close()
    conn.close()

    return {
        "access_token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": "admin" if user["is_admin"] else "user",
            "can_view_all": user["can_view_all"]
        }
    }
