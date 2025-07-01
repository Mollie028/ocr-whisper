# main.py
import os
from fastapi import FastAPI
import uvicorn

# 移除所有其他導入語句，包括 FastApi.middleware.cors 等
# from backend.api import auth, ocr, whisper
# from backend.services.ocr_service import initialize_ocr_model
# from backend.services.whisper_service import initialize_whisper_model

app = FastAPI()

# 移除所有 @app.on_event("startup") 裝飾器和相關函數
# 移除所有 app.add_middleware()
# 移除所有 app.include_router()
# 移除任何其他您自行定義的函數，例如 _keep_alive()

@app.get("/")
async def root():
    # 僅返回一個最簡單的字串，不進行任何計算或外部調用
    return {"message": "Hello from Railway! - Super Minimal Test Confirmed!"}

if __name__ == "__main__":
    # 從環境變數獲取 PORT，如果沒有則預設 8000
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
