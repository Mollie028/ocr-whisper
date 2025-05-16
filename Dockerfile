FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libgomp1 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .


# 用 uvicorn 啟動 FastAPI 應用，注意：不要手寫 port 數字
CMD ["python", "-m", "uvicorn", "ocr_api:app", "--host", "0.0.0.0", "--port", "8000"]


