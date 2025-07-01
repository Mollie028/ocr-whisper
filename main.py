import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 暫時註釋掉所有模組導入，除非極簡測試成功後再逐步恢復
# from backend.api import auth, ocr, whisper
# from backend.services.ocr_service import initialize_ocr_model
# from backend.services.whisper_service import initialize_whisper_model


# API_BASE = "https://ocr-whisper-api-production-03e9.up.railway.app/" # 這個變數在應用程式內部通常不需要，或者應該透過環境變數傳入

app = FastAPI()

# 暫時註釋掉 CORS 設定，以排除其對基本連通性的影響
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 可改為前端網址
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# 暫時註釋掉所有 API 路由註冊
# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
# app.include_router(whisper.router, prefix="/whisper", tags=["whisper"])

# 啟動事件：徹底清空啟動事件中的邏輯，特別是 keep-alive，以排除其干擾
@app.on_event("startup")
async def startup_event():
    # 這裡只保留一個簡單的 print 語句
    print("🚀 應用啟動：極簡測試模式。")
    # 確保沒有任何阻塞或循環的邏輯在這裡
    # loop = asyncio.get_event_loop()
    # loop.create_task(_keep_alive())
    # await asyncio.to_thread(initialize_ocr_model)
    # await asyncio.to_thread(initialize_whisper_model)

# 暫時註釋掉 _keep_alive 函數，以排除其影響
# async def _keep_alive():
#     while True:
#         print("💡 still alive...")
#         await asyncio.sleep(3600)

# 最簡化的根路徑，確保它只返回一個簡單的 JSON
@app.get("/")
async def root():
    return {"message": "Hello from Railway! - Minimal Test OK!"}

# 確保只運行一次 uvicorn
if __name__ == "__main__":
    # 從環境變數獲取 PORT，如果沒有則預設 8000
    port = int(os.getenv("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
