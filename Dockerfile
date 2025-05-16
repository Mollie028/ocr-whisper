FROM python:3.10-slim

# 安裝系統套件（包含 libGL.so.1）
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 建立工作目錄
WORKDIR /app

# 複製需求檔與程式碼
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 啟動 FastAPI
CMD ["uvicorn", "ocr_api:app", "--host", "0.0.0.0", "--port", "8000"]
