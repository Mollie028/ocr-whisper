from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.ocr_service import run_ocr
from backend.services.extract_service import extract_fields_from_text
from backend.core.db import get_conn  


import datetime

router = APIRouter(prefix="/ocr", tags=["OCR 名片辨識"])

@router.post("/")
async def ocr_card(file: UploadFile = File(...)):
    # 驗證檔案格式
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="請上傳圖片格式（jpg, png）")

    # 1. OCR 辨識文字
    text = await run_ocr(file)

    # 2. 傳送給 LLaMA 進行欄位抽取
    fields = extract_fields_from_text(text)

    # 3. 寫入資料庫
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO business_cards (name, title, email, phone, company, raw_text, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            fields.get("name"),
            fields.get("title"),
            fields.get("email"),
            fields.get("phone"),
            fields.get("company_name"),
            text,
            datetime.datetime.utcnow()
        )
    )
    conn.commit()
    cur.close()
    conn.close()

    return {
        "message": "✅ OCR 成功，並完成欄位萃取與儲存",
        "fields": fields
    }
