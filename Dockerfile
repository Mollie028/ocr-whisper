# 使用輕量級 Python 映像
FROM python:3.9-slim

# 安裝 PaddleOCR 執行時所需的系統套件
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgomp1 \
    ttf-wqy-zenhei \  # ✅ 安裝中文字型以支援中文OCR
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製 requirements 並安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個專案到容器中
COPY . .

# 預設啟動 FastAPI 使用 gunicorn + uvicorn worker
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--worker-class", "uvicorn.workers.UvicornWorker", "main:app"]
