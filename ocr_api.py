from fastapi.security import OAuth2PasswordBearer
from backend.core.security import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from backend.schemas.user import UserCreate, UserLogin, Token

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
from faster_whisper import WhisperModel
from PIL import Image
import numpy as np
import cv2
import io
import tempfile
import os
import requests
import psycopg2
import json
import socket

# ───── Debug DNS ──────
print("→ DEBUG: DB_HOST =", os.getenv("DB_HOST"))
try:
    ip = socket.gethostbyname(os.getenv("DB_HOST") or "")
    print(f"→ DEBUG: DNS OK, {os.getenv('DB_HOST')} → {ip}")
except Exception as e:
    print(f"→ DEBUG: DNS ERROR resolving {os.getenv('DB_HOST')}: {e}")
# ─────────────────────

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───── 是否跳過模型下載 ─────
SKIP_MODEL_LOAD = os.getenv("SKIP_MODEL_LOAD", "false").lower() == "true"
if not SKIP_MODEL_LOAD:
    ocr_model = PaddleOCR(use_angle_cls=True, lang='ch', det_db_box_thresh=0.3)
    whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
else:
    ocr_model = None
    whisper_model = None
# ───────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

DB_CONFIG = {
    "host":     os.getenv("DB_HOST"),
    "port":     os.getenv("DB_PORT"),
    "dbname":   os.getenv("DB_NAME"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "sslmode":  "require"
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

# ───── 自動建表 ─────
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            role VARCHAR(10) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

try:
    init_db()
    print("→ INFO: init_db succeeded")
except Exception as e:
    print(f"→ WARN: init_db failed: {e}")
# ──────────────────────

# 🧠 你的 API 功能（register、login、ocr、whisper、extract）這裡都不需要改動
# ✅ 留下你原本的功能即可，保持穩定，避免再貼一大段干擾你辨識

# ⚠️ 如果你要我一起幫你完整整理所有 endpoint，請再告訴我
