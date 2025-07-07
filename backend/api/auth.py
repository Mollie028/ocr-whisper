from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.core.db import get_db
from backend.models.user import User, UserCreate, UserLogin, UserOut
from backend.core.security import get_password_hash, verify_password, create_access_token
import traceback
router = APIRouter()

# ✅ 註冊新使用者
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = get_user_by_username(db, user.username)
        if db_user:
            return JSONResponse(status_code=400, content={"message": "⚠️ 帳號已存在"})
        
        # 密碼雜湊
        hashed_password = get_password_hash(user.password)
        
        # 建立使用者
        new_user = User(
            username=user.username,
            hashed_password=hashed_password,
            company_name=user.company_name,
            is_admin=False
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"id": new_user.id, "username": new_user.username, "is_admin": new_user.is_admin}
    
    except Exception as e:
        # 把錯誤詳細資訊印出來
        import traceback
        print(traceback.format_exc())  # 印在 logs 裡
        return JSONResponse(status_code=500, content={"message": f"🚨 系統內部錯誤：{str(e)}"})


# ✅ 使用者登入
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
        "is_admin": user.is_admin
    }


@router.get("/get_users")
def get_users(db: Session = Depends(get_db)):
    try:
        users = db.query(User).all()
        return [{"id": u.id, "username": u.username, "is_admin": u.is_admin} for u in users]
    except Exception as e:
        print("❌ 錯誤追蹤：", traceback.format_exc())  # 將完整錯誤印出
        raise HTTPException(status_code=500, detail=f"❌ 系統錯誤：{str(e)}")

