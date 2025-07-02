FROM python:3.9-slim

# 安裝必要套件（避免 libpng/libjpeg 錯誤）
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# 建立工作目錄
WORKDIR /app

# 複製 requirements 並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有專案程式碼
COPY . .

# 使用 gunicorn 啟動 FastAPI
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--worker-class", "uvicorn.workers.UvicornWorker", "main:app"]
