from fastapi import FastAPI, UploadFile, File, HTTPException
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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ocr_model = PaddleOCR(use_angle_cls=True, lang='ch', det_db_box_thresh=0.3)
whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT")
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def clean_ocr_text(result):
    lines = []
    try:
        if isinstance(result, list):
            for entry in result:
                texts = entry.get("rec_texts", [])
                for t in texts:
                    t = t.strip()
                    if t and not any(x in t.lower() for x in ["www", "fax", "網址", "傳真"]):
                        lines.append(t)
    except Exception as e:
        print("❌ clean_ocr_text 錯誤：", e)
    cleaned = "\n".join(lines)
    print("最終擷取內容：", repr(cleaned))
    return cleaned

@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...), user_id: int = 1):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        MAX_SIDE = 1600
        height, width = img.shape[:2]
        max_side = max(height, width)
        if max_side > MAX_SIDE:
            scale = MAX_SIDE / max_side
            new_w = int(width * scale)
            new_h = int(height * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        result = ocr_model.ocr(img)
        final_text = clean_ocr_text(result)

        if not final_text:
            raise HTTPException(status_code=400, detail="❌ OCR 沒有辨識出任何內容")

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO business_cards (user_id, ocr_text) VALUES (%s, %s) RETURNING id", (user_id, final_text))
        record_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return {"id": record_id, "text": final_text}
    except Exception as e:
        import traceback
        print("❌ OCR 發生錯誤：", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"OCR 發生錯誤：{e}")

@app.post("/whisper")
async def whisper_endpoint(file: UploadFile = File(...), user_id: int = 1):
    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        segments, _ = whisper_model.transcribe(
            tmp_path, language="zh", beam_size=1, vad_filter=True, max_new_tokens=440
        )
        text = " ".join([seg.text.strip() for seg in segments])

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO business_cards (user_id, ocr_text) VALUES (%s, %s) RETURNING id", (user_id, text))
        record_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return {"id": record_id, "text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Whisper 發生錯誤：{e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
