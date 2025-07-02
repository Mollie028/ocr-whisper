FROM python:3.9-slim

# 安裝系統相依套件
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgomp1 \
    ttf-wqy-zenhei \
    && rm -rf /var/lib/apt/lists/*

# 建立並切換工作目錄
WORKDIR /app

# 複製需求檔並安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個專案進來
COPY . .

# 使用 gunicorn 啟動 FastAPI 應用（位於 main.py）
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "main:app"]
