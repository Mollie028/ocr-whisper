from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.core.db import get_db
from backend.models.user import User, UserCreate, UserLogin, UserOut
from backend.core.security import get_password_hash, verify_password, create_access_token
from backend.services.user_service import get_user_by_username
from pydantic import BaseModel
import traceback

router = APIRouter()

# ✅ 註冊新使用者（包含 is_admin 參數）
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = get_user_by_username(db, user.username)
        if db_user:
            return JSONResponse(status_code=400, content={"message": "⚠️ 帳號已存在"})

        # 依據前端傳入的 is_admin 決定權限
        is_admin = user.is_admin if hasattr(user, "is_admin") else False

        hashed_password = get_password_hash(user.password)

        new_user = User(
            username=user.username,
            password_hash=hashed_password,
            company_name=user.company_name,
            is_admin=user.is_admin
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "id": new_user.id,
            "username": new_user.username,
            "is_admin": new_user.is_admin
        }

    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"message": f"🚨 系統內部錯誤：{str(e)}"})


@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="❌ 帳號或密碼錯誤")

    token = create_access_token(data={
        "sub": user.username,
        "is_admin": user.is_admin
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "is_admin": user.is_admin,
        "company_name": user.company_name,
        "role": "admin" if user.is_admin else "user"
    }



# ✅ 取得所有使用者（給管理員查詢用）
@router.get("/get_users")
def get_users(company_name: str = "", db: Session = Depends(get_db)):
    try:
        if company_name:
            users = db.query(User).filter(User.company_name == company_name).all()
        else:
            users = db.query(User).all()
        return [{"id": u.id, "username": u.username, "is_admin": u.is_admin} for u in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ 系統錯誤：{str(e)}")


class UpdateUserRole(BaseModel):
    username: str
    is_admin: bool

@router.post("/update_role")
def update_user_role(data: UpdateUserRole, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="使用者不存在")
    
    user.is_admin = data.is_admin
    db.commit()
    return {"message": "使用者權限已更新", "is_admin": user.is_admin}

