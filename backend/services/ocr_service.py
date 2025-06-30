# backend/services/ocr_service.py
from paddleocr import PaddleOCR
import numpy as np
import cv2
from PIL import Image
import io

ocr_model_instance = None

def initialize_ocr_model():
    global ocr_model_instance
    if ocr_model_instance is None:
        print("🚀 初始化 PaddleOCR 模型（mobile）...")
        try:
            ocr_model_instance = PaddleOCR(
                use_angle_cls=False,  # ✅ 停用 angle classifier，省記憶體
                lang='ch',            # ✅ 中文
                use_gpu=False         # ✅ 強制用 CPU，避免 GPU 掃描報錯
            )
            print("✅ PaddleOCR 初始化完成！")
        except Exception as e:
            print(f"❌ 初始化失敗: {e}")
            raise
    return ocr_model_instance

# ... (run_ocr 函數及其他部分保持不變)

async def run_ocr(file):
    # 確保模型已初始化
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
        if result and result[0]: # 檢查 result 和 result[0] 是否存在
            for box in result[0]:
                text = box[1][0].strip()
                if text and not any(x in text.lower() for x in ["www", "fax", "網址", "傳真"]):
                    lines.append(text)
    except Exception as e:
        print(f"❌ OCR 擷取失敗：{e}")
    return " ".join(lines)
