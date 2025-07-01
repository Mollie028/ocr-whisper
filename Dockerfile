FROM python:3.11-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    gcc build-essential python3-dev pkg-config curl \
    && apt-get clean

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# ⚠️ 很重要！這個讓 FastAPI 找得到 backend 裡的模組
ENV PYTHONPATH=/app

EXPOSE 8000

# 不要加 --app-dir，因為 main.py 就在 /app 根目錄
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
