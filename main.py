from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from backend.api import auth, ocr, whisper
from backend.core.db import engine
from backend.models.user import Base
import logging
import sys
import os

# -------------------
# ✅ Logging 設定
# -------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# -------------------
# ✅ 自動建立資料表（只會執行一次）
# -------------------
Base.metadata.create_all(bind=engine)

# -------------------
# ✅ FastAPI 初始化
# -------------------
app = FastAPI()

# -------------------
# ✅ CORS 設定
# -------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 建議換成你的前端網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------
# ✅ 註冊路由
# -------------------
app.include_router(auth.router)
app.include_router(ocr.router)
app.include_router(whisper.router)

# -------------------
# ✅ 例外錯誤處理
# -------------------
@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"❗ 系統錯誤：{e}", exc_info=True)
        return JSONResponse(status_code=500, content={"message": "🚨 系統內部錯誤"})

@app.get("/")
def health_check():
    return {"message": "✅ API 正常運作中！"}

@app.on_event("startup")
async def on_startup():
    logger.info("🚀 FastAPI 正在啟動...")
    port = os.getenv("PORT", "8000")
    logger.info(f"環境 PORT: {port}")
