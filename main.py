import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import auth, ocr, whisper
from backend.services.ocr_service import initialize_ocr_model
from backend.services.whisper_service import initialize_whisper_model


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
    print("🚀 應用啟動：載入模型")
    loop = asyncio.get_event_loop()
    loop.create_task(_keep_alive())
    await asyncio.to_thread(initialize_ocr_model)
    await asyncio.to_thread(initialize_whisper_model)

async def _keep_alive():
    while True:
        print("💡 still alive...")
        await asyncio.sleep(3600)

@app.get("/")
def health_check():
