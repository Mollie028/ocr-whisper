from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.core.db import get_db
from backend.models.user import User, UserCreate, UserLogin, UserOut, UserUpdate
from backend.core.security import get_password_hash, verify_password, create_access_token, get_current_user
from backend.services.user_service import get_user_by_username, get_all_users, get_user_by_id

router = APIRouter()

# ✅ 註冊
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="⚠️ 帳號已存在")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        password_hash=hashed_password,
        company_name=user.company_name or "",
        is_admin=user.is_admin or False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "id": new_user.id,
        "username": new_user.username,
        "is_admin": new_user.is_admin
    }

# ✅ 登入
@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_username(db, login_data.username)
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="❌ 帳號或密碼錯誤")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="⛔️ 帳號已被停用")
    
    token = create_access_token({"sub": user.username, "is_admin": user.is_admin})
    return {
        "access_token": token,
        "token_type": "bearer",
        "is_admin": user.is_admin,
        "company_name": user.company_name,
        "role": "admin" if user.is_admin else "user"
    }

# ✅ 取得所有使用者帳號清單
@router.get("/users", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    try:
        users = get_all_users(db)
        for u in users:
            print("🧑", u.username, "| role:", u.role)
        return users
    except Exception as e:
        import traceback
        print("❌ 錯誤發生在 /users：", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="🚨 系統內部錯誤")

# ✅ 新增：更新使用者資料（備註、權限、狀態）
@router.put("/update_user/{user_id}")
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="找不到使用者")

    # 權限檢查：只能修改自己或是管理員可修改他人
    if current_user.id != user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="⛔️ 權限不足，無法修改他人帳號")

    # 不能修改管理員的權限與狀態（除非你是自己）
    if user.is_admin and current_user.id != user.id:
        raise HTTPException(status_code=403, detail="⛔️ 無法修改管理員帳號")

    user.note = user_update.note
    user.is_admin = user_update.is_admin
    user.is_active = user_update.is_active

    db.commit()
    db.refresh(user)
    return {
        "message": "✅ 使用者資料已更新",
        "user_id": user.id,
        "username": user.username
    }
