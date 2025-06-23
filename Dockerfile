FROM python:3.11-slim

WORKDIR /app

# 安裝 libgl1 給 OpenCV 用
RUN apt-get update && apt-get install -y libgl1

# 複製 requirements 並安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有程式碼
COPY . /app

# 設定 PYTHONPATH，讓 backend 可以被正確引用
ENV PYTHONPATH=/app

# 執行 FastAPI 伺服器
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
