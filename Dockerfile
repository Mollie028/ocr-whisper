# 使用輕量級的 Python 基底映像
FROM python:3.10-slim

# 安裝 libgl1、libgomp（這是 PaddleOCR 需要的依賴）
RUN apt-get update && apt-get install -y \
    libgl1 \
    libgomp1 \
    libglib2.0-0 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製依賴檔案並安裝
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt || cat /app/requirements.txt

# 複製主程式
COPY "ocr_api:app" .

# 啟動 FastAPI 應用
CMD ["python", "ocr_api:app"]

