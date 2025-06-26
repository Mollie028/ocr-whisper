import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio # 導入 asyncio

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

# 在應用程式啟動時載入模型
@app.on_event("startup")
async def startup_event():
    print("💡 執行應用程式啟動事件...")
    # 由於模型載入是 CPU 密集型操作，可能不是完全異步的，
    # 我們可以使用 asyncio.to_thread 來避免阻塞 FastAPI 的事件循環
    #await asyncio.to_thread(initialize_ocr_model)
    #await asyncio.to_thread(initialize_whisper_model)
    print("🎉 所有模型初始化完成！應用程式已準備好。")

# 根目錄健康檢查
@app.get("/")
def health_check():
    return {"message": "✅ API is alive"}
