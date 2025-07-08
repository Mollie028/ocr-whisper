from sqlalchemy.orm import Session
from backend.models.user import User, UserCreate
from backend.core.security import get_password_hash, verify_password

# 查詢使用者 by username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# 建立新使用者（已加入 is_admin 和 can_view_all 欄位）
def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)

    # 新增權限欄位
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        is_admin=user.is_admin,
        can_view_all=user.can_view_all,
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
