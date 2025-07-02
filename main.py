# main.py
import os
import logging
import sys # 新增導入
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
# 不需要在這裡 import uvicorn 了，因為它會通過 CMD 命令直接調用

# 配置 logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout) # 強制輸出到 stdout
logger = logging.getLogger(__name__)

app = FastAPI()

# 全局錯誤處理中間件
@app.middleware("http")
async def catch_exceptions_middleware(request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled exception caught by middleware: {e}", exc_info=True)
        sys.stderr.flush() # 強制刷新錯誤日誌
        return JSONResponse(content={"message": "Internal Server Error"}, status_code=500)

# 根路徑
@app.get("/")
async def root():
    logger.info("Received GET / request.")
    sys.stdout.flush() # 強制刷新標準輸出
    return {"message": "Hello from Railway! - Super Minimal Test Confirmed - Direct CMD!"}

# 啟動事件
@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application is starting up.")
    sys.stdout.flush() # 強制刷新標準輸出
    try:
        test_val = os.getenv("PORT", "8000")
        logger.info(f"Environment PORT variable: {test_val}")
        sys.stdout.flush() # 強制刷新標準輸出
    except Exception as e:
        logger.error(f"Error accessing environment variable: {e}", exc_info=True)
        sys.stderr.flush() # 強制刷新錯誤日誌
    logger.info("FastAPI application startup complete and ready to receive requests.")
    sys.stdout.flush() # 強制刷新標準輸出

# 移除 if __name__ == "__main__": 塊，讓 CMD 直接啟動
# (確保您的 main.py 文件中，沒有這個塊)
