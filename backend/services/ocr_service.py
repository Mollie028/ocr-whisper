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
        print("🚀 初始化 PaddleOCR 模型...")

        try:
            ocr_model_instance = PaddleOCR(
                use_angle_cls=True,  # 仍然使用角度分類
                lang='ch',           # 仍然是中文
                use_gpu=False,       # 顯式關閉 GPU 使用，確保在 CPU 上運行，避免 GPU 相關記憶體分配
                show_log=False       # 關閉 PaddleOCR 的內部日誌，讓我們的日誌更清晰
                
            )
            print("✅ PaddleOCR 模型初始化完成 (可能為輕量級模型)。")
        except Exception as e:
            print(f"❌ PaddleOCR 模型初始化失敗: {e}")
            # 如果初始化失敗，嘗試使用更通用的 fallback 方式 (如果需要)
            # 但現在重點是解決 OOM，所以先專注於輕量級配置
            raise # 重新拋出異常，讓部署失敗以便診斷
        
    return ocr_model_instance

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
        # 如果這裡發生錯誤，可能意味著 OCR 辨識結果的結構有問題
        # 為了避免應用程式完全崩潰，可以考慮回傳空字串或更詳細的錯誤訊息
    return " ".join(lines)
