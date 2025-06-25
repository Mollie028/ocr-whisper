echo "🚀 Running entrypoint.sh"

# 啟動 API 主程式
exec uvicorn backend.main:app --host=0.0.0.0 --port=8000
