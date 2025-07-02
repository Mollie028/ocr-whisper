# Dockerfile
FROM python:3.11-buster

WORKDIR /app

# 精簡 apt-get install，只保留 PyMuPDF / MuPDF 運行時可能需要的核心依賴
# 這些是為了讓預編譯的 PyMuPDF wheel 能夠正確運行，而不是為了編譯源碼
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libharfbuzz0b \
        libfreetype6 \
        libfontconfig1 \
        libjpeg62-turbo \ # <-- **這個是關鍵，確認是這個名稱**
        libpng16-16 \
        zlib1g \
        # 如果 paddleocr 在運行時有其他系統依賴，可以視情況再加入
        # 但現在先最小化，以排除 PyMuPDF 編譯問題
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式代碼
COPY . .

# 設定環境變數，告知 Uvicorn 監聽 8000 埠 (Railway 會透過 PORT 變數自動映射)
ENV PORT 8000

# 暴露埠 (可選，但建議保留)
EXPOSE 8000


# 啟動應用程式
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "1", "main:app"]
