FROM python:3.11-slim-buster

# 設定環境變數，讓構建過程不詢問任何互動式問題
ENV DEBIAN_FRONTEND=noninteractive


RUN apt-get update && apt-get install -y \
    build-essential \
    libmupdf-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    poppler-utils \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    pkg-config \
    cmake \
    zlib1g-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    && rm -rf /var/lib/apt/lists/*
# 設定工作目錄
WORKDIR /app

# 將 requirements.txt 複製到容器中並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 將應用程式代碼複製到容器中
COPY . .

# 設定環境變數 PORT，讓應用程式監聽 Railway 提供的端口
ENV PORT 8000

# 暴露應用程式監聽的端口
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
