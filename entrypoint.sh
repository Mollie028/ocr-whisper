#!/bin/bash

echo "🚀 Running entrypoint.sh"

exec uvicorn backend.main:app --host=0.0.0.0 --port=8000
