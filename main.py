# main.py
import os
import logging
import sys
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
# from backend.api import auth, ocr, whisper # 註解掉
# from backend.services.ocr_service import initialize_ocr_model # 註解掉
# from backend.services.whisper_service import initialize_whisper_model # 註解掉

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.middleware("http")
async def catch_exceptions_middleware(request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled exception caught by middleware: {e}", exc_info=True)
        sys.stderr.flush()
        return JSONResponse(content={"message": "Internal Server Error"}, status_code=500)

@app.get("/")
async def root():
    logger.info("Received GET / request.")
    sys.stdout.flush()
    return {"message": "Hello from Railway! - Minimal Test OK - Without Models!"} # 更改訊息以區分

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application is starting up.")
    sys.stdout.flush()
    try:
        test_val = os.getenv("PORT", "8000")
        logger.info(f"Environment PORT variable: {test_val}")
        sys.stdout.flush()
    except Exception as e:
        logger.error(f"Error accessing environment variable: {e}", exc_info=True)
        sys.stderr.flush()
    logger.info("FastAPI application startup complete and ready to receive requests.")
    sys.stdout.flush()

# 如果有 _keep_alive 函數，也暫時註解掉或確保它在 startup_event 中未被調用
# async def _keep_alive():
#     while True:
#         print("💡 still alive...")
#         await asyncio.sleep(3600)
