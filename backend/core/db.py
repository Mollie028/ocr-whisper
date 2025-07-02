import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 讀取環境變數中的 DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("❌ DATABASE_URL 未設定")

# 建立 SQLAlchemy 的 Engine、SessionLocal 和 Base 類別
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 提供給 FastAPI 的 DB Session 相依注入函式
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
