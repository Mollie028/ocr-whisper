FROM python:3.11-slim-buster

WORKDIR /app

# 安裝必要系統相依套件
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    gcc build-essential python3-dev pkg-config curl wget \
    libssl1.1 \
    && apt-get clean

# 安裝 libssl1.1（避免 whisper / requests / Paddle 出現 SSL 問題）
RUN wget http://security.ubuntu.com/ubuntu/pool/main/o/openssl1.1/libssl1.1_1.1.1f-1ubuntu2.22_amd64.deb && \
    dpkg -i libssl1.1_1.1.1f-1ubuntu2.22_amd64.deb && \
    rm libssl1.1_1.1.1f-1ubuntu2.22_amd64.deb

# 複製 requirements 並安裝
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 安裝 paddleocr（不加 --no-deps，讓他自動補齊相依）
RUN pip install paddleocr==2.6.1.3

# 複製程式碼
COPY . .

# 設定 PYTHONPATH（你的 main.py 在 /app，api 與 services 也在這層）
ENV PYTHONPATH=/app

EXPOSE 8000

# 啟動指令（你已將 main.py 放在根目錄）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
