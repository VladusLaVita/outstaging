#!/usr/bin/env bash
echo "🛑 Остановка Knowledge Base..."
docker stop qdrant 2>/dev/null || true
pkill -f "python.*api.py" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
pkill -f "webhook-listener.py" 2>/dev/null || true
echo "✅ Всё остановлено."