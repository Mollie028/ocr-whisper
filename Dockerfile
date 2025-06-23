# 使用官方 Python 基礎映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製依賴與程式碼
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./backend ./backend

# 開放埠口
EXPOSE 8000

# 啟動 FastAPI 應用（main.py）
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
