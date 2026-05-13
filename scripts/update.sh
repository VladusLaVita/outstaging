#!/usr/bin/env bash
set -euo pipefail

# 🎨 Цвета для вывода
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

# Пути (из .env или дефолтные)
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PYTHON_DIR="$PROJECT_ROOT/rag/knowledge-base"
SITE_DIR="$PROJECT_ROOT/site"
VENV="$PYTHON_DIR/venv/bin/activate"

echo -e "${GREEN}🔄 Начало обновления...${NC}"
echo "   Проект: $PROJECT_ROOT"

# 1️⃣ Git pull
echo -e "\n${YELLOW}📥 git pull...${NC}"
cd "$PROJECT_ROOT"
git pull origin main
echo -e "   ✅ Код обновлён"

# 2️⃣ Синхронизация статей
echo -e "\n${YELLOW}🔄 Синхронизация статей...${NC}"
cd "$PROJECT_ROOT"
source "$VENV"
python3 site/sync.py
echo -e "   ✅ Статьи синхронизированы"

# 3️⃣ Сборка фронтенда
echo -e "\n${YELLOW}📦 Сборка фронтенда...${NC}"
cd "$SITE_DIR"
npm run build
echo -e "   ✅ Сборка завершена"

# 4️⃣ Деплой на VPS
echo -e "\n${YELLOW}🚀 Деплой на VPS...${NC}"
VPS_USER="${VPS_USER:-root}"
VPS_HOST="${VPS_HOST:-86.110.194.68}"
SSH_KEY="${VPS_SSH_KEY:-~/.ssh/kb_vps}"
rsync -avz --delete -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
    docs/.vitepress/dist/ \
    ${VPS_USER}@${VPS_HOST}:/var/www/swinki.ru/dist/
echo -e "   ✅ Файлы задеплоены"

# 5️⃣ Переиндексация
echo -e "\n${YELLOW}🧠 Переиндексация базы...${NC}"
cd "$PYTHON_DIR"
source "$VENV"
python3 ingest.py
echo -e "   ✅ Индексация завершена"

# 6️⃣ Перезапуск сервисов (опционально)
# echo -e "\n${YELLOW}🔄 Перезапуск сервисов...${NC}"
# pkill -f "python.*api.py" && sleep 1 && python3 api.py &
# echo -e "   ✅ Сервисы перезапущены"

echo -e "\n${GREEN}✅ Обновление завершено!${NC}"
echo "   🌐 Сайт: https://swinki.ru"
echo "   🤖 API:  https://swinki.ru/api/ask"
