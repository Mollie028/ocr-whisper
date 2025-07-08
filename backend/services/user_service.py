from sqlalchemy.orm import Session
from backend.models.user import User, UserCreate
from backend.core.security import get_password_hash, verify_password

# 查詢使用者 by username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)

    # 根據輸入角色給予不同權限
    is_admin = user.role == "admin"
    can_view_all = user.role in ["admin", "viewer"]  # 如果你有 viewer 權限

    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        company_name=user.company_name,
        is_admin=is_admin,
        can_view_all=can_view_all
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# 登入驗證
def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
