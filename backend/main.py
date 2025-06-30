import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio 

app = FastAPI()

# 模組匯入：依照專案結構 backend/api/*
from backend.api import auth, ocr, whisper
from backend.services.ocr_service import initialize_ocr_model
from backend.services.whisper_service import initialize_whisper_model

API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app/" 

# CORS 設定（允許前端跨網域請求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 部署完成後可改為前端網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由註冊
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
app.include_router(whisper.router, prefix="/whisper", tags=["whisper"])



@app.on_event("startup")
async def keep_alive():
    print("🚀 啟動 keep-alive 任務")
    asyncio.create_task(_keep_alive())

async def _keep_alive():
    while True:
        await asyncio.sleep(3600)


# 根目錄健康檢查
@app.get("/")
def health_check():
    return {"message": "✅ API is alive"}
