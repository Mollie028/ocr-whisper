from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.ocr_service import run_ocr
from backend.services.extract_service import extract_fields_from_llm
from backend.core.db import get_conn
from datetime import datetime

router = APIRouter(prefix="/ocr", tags=["OCR 名片辨識"])


@router.post("/")
async def ocr_card(file: UploadFile = File(...)):
    # 1. 驗證檔案格式
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="請上傳 jpg、jpeg 或 png 格式圖片")

    try:
        # 2. 執行 OCR
        text = await run_ocr(file)

        # 3. 使用 LLM 萃取欄位
        fields = extract_fields_from_llm(text)

        # 4. 寫入資料庫
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO business_cards (name, title, email, phone, company_name, raw_text, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                fields.get("name"),
                fields.get("title"),
                fields.get("email"),
                fields.get("phone"),
                fields.get("company_name"),
                text,
                datetime.utcnow()
            )
        )
        record_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        # 5. 回傳結果
        return {
            "message": "✅ OCR 成功，欄位已萃取並儲存",
            "record_id": record_id,
            "fields": fields,
            "raw_text": text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ 發生錯誤：{str(e)}")
