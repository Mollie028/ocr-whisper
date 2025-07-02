# main.py
import os
import logging
from fastapi import FastAPI
import uvicorn

# 配置 logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# 根路徑
@app.get("/")
async def root():
    logger.info("Received GET / request.") # 添加日誌
    return {"message": "Hello from Railway! - Super Minimal Test Confirmed!"}

# 添加一個 startup 事件，用於輸出更明確的啟動日誌
@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application is starting up.")
    # 在這裡可以嘗試執行一些非常簡單的操作，確保環境正常
    try:
        test_val = os.getenv("PORT", "8000")
        logger.info(f"Environment PORT variable: {test_val}")
    except Exception as e:
        logger.error(f"Error accessing environment variable: {e}")
    logger.info("FastAPI application startup complete and ready to receive requests.")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Uvicorn will run on 0.0.0.0:{port}") # 添加日誌
    uvicorn.run(app, host="0.0.0.0", port=port)
