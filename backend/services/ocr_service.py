# backend/services/ocr_service.py

from paddleocr import PaddleOCR
import numpy as np
import cv2
from PIL import Image
import io

# 初始化 PaddleOCR（建議只初始化一次）
ocr_model = PaddleOCR(use_angle_cls=True, lang='ch', det_db_box_thresh=0.3)

async def run_ocr(file):
    # 讀取圖片內容
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # 圖片太大就縮小
    MAX_SIDE = 1600
    height, width = img.shape[:2]
    max_side = max(height, width)
    if max_side > MAX_SIDE:
        scale = MAX_SIDE / max_side
        new_w = int(width * scale)
        new_h = int(height * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # 執行 OCR
    result = ocr_model.ocr(img, cls=True)

    # 擷取文字內容
    lines = []
    try:
        for box in result[0]:
            text = box[1][0].strip()
            if text and not any(x in text.lower() for x in ["www", "fax", "網址", "傳真"]):
                lines.append(text)
    except Exception as e:
        print("❌ OCR 擷取失敗：", e)

    final_text = "\n".join(lines)
    return final_text
