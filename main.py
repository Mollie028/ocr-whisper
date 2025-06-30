import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import auth, ocr, whisper
from services.ocr_service import initialize_ocr_model
from services.whisper_service import initialize_whisper_model


API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app/"

app = FastAPI()

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可改為前端網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由註冊
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
app.include_router(whisper.router, prefix="/whisper", tags=["whisper"])

# 啟動事件：初始化模型 & keep-alive
@app.on_event("startup")
async def startup_event():
    print("🚀 應用啟動：載入模型 & 啟動 keep-alive")
    loop = asyncio.get_event_loop()
    loop.create_task(_keep_alive())

    # 初始化模型（用 asyncio.to_thread 避免阻塞）
    await asyncio.to_thread(initialize_ocr_model)
    await asyncio.to_thread(initialize_whisper_model)
    print("🎉 所有模型初始化完成")

# keep-alive 偵測
async def _keep_alive():
    while True:
        print("💡 still alive...")
        await asyncio.sleep(3600)

# 健康檢查路由
@app.get("/")
def health_check():
    return {"message": "✅ API is alive"}
