# backend/services/ocr_service.py
from paddleocr import PaddleOCR
import numpy as np
import cv2
from PIL import Image
import io

# 宣告一個變數來存放模型，初始為 None
ocr_model_instance = None

def initialize_ocr_model():
    global ocr_model_instance
    if ocr_model_instance is None:
        print("🚀 初始化 PaddleOCR 模型...")
        ocr_model_instance = PaddleOCR(use_angle_cls=True, lang='ch', det_db_box_thresh=0.3)
        print("✅ PaddleOCR 模型初始化完成。")
    return ocr_model_instance

async def run_ocr(file):
    model = initialize_ocr_model() # 這裡現在會取得初始化過後的模型

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

    result = model.ocr(img, cls=True)

    lines = []
    try:
        for box in result[0]:
            text = box[1][0].strip()
            if text and not any(x in text.lower() for x in ["www", "fax", "網址", "傳真"]):
                lines.append(text)
    except Exception as e:
        print(f"❌ OCR 擷取失敗：{e}")
    return " ".join(lines)
