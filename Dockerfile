# 使用輕量級 Python 映像
FROM python:3.10-slim

# 安裝 PaddleOCR 所需系統套件
RUN apt-get update && apt-get install -y \
    libgl1 \
    libgomp1 \
    libglib2.0-0 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製 requirements 並安裝（使用 no-cache-dir，加速且避免中斷）
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt -i https://pypi.org/simple

# 複製整個應用程式原始碼
COPY . .

# 使用 uvicorn 執行 FastAPI
CMD ["python", "-m", "uvicorn", "ocr_api:app", "--host", "0.0.0.0", "--port", "8000"]
