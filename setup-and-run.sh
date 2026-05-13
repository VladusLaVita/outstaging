#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$PROJECT_DIR/rag/knowledge-base"
SITE_DIR="$PROJECT_DIR/site"

# 🤖 Модель
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5:7b}"

echo -e "${GREEN}========================================================"
echo -e "   Полная установка и запуск Knowledge Base"
echo -e "========================================================${NC}\n"

cd "$PROJECT_DIR" || exit

# 1️⃣ Сервисы
echo -e "[1/6] ${YELLOW}Проверка Docker и Ollama...${NC}"
if ! docker ps &>/dev/null; then
    echo -e "   ${RED}⚠️ Docker не запущен! Откройте Docker Desktop и повторите.${NC}"
    exit 1
fi
docker start qdrant 2>/dev/null || docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
curl -s http://localhost:11434 &>/dev/null || echo -e "   ⚠️ Ollama не отвечает. Запустите: ollama serve"

# Модель
echo -e "[2/6] ${YELLOW}Модель $OLLAMA_MODEL...${NC}"
if ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
    echo -e "   ✅ Уже установлена"
else
    echo -e "   ⬇️ Скачиваем (~4.2 ГБ)... Ожидайте."
    ollama pull "$OLLAMA_MODEL"
    echo -e "   ✅ Готово"
fi
echo

# 2️⃣ Backend
echo -e "[3/6] ${YELLOW}Настройка Python backend...${NC}"
cd "$PYTHON_DIR" || exit
[ -d "venv" ] && rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
else
    pip install flask flask-cors requests llama-index llama-index-core llama-index-embeddings-ollama llama-index-llms-ollama llama-index-vector-stores-qdrant==0.1.4 "numpy<2" python-dotenv pypdf -q
fi
echo -e "   ✅ Backend готов.\n"

# 3️⃣ Данные
echo -e "[4/6] ${YELLOW}Синхронизация статей...${NC}"
cd "$SITE_DIR" || exit
python3 sync.py
echo

echo -e "[5/6] ${YELLOW}Индексация в Qdrant...${NC}"
cd "$PYTHON_DIR" || exit
python3 ingest.py
echo

# 4️⃣ Frontend
echo -e "[6/6] ${YELLOW}Настройка Frontend...${NC}"
cd "$SITE_DIR" || exit
[ -d "node_modules" ] && rm -rf node_modules
npm install
echo -e "   ✅ Frontend готов.\n"

# 5️⃣ Запуск
echo -e "${YELLOW}✨ Запуск серверов...${NC}"

detect_terminal() {
    if command -v cosmic-term &>/dev/null; then echo "cosmic"
    elif command -v gnome-terminal &>/dev/null; then echo "gnome"
    elif command -v konsole &>/dev/null; then echo "konsole"
    elif command -v alacritty &>/dev/null; then echo "alacritty"
    elif command -v kitty &>/dev/null; then echo "kitty"
    elif command -v xterm &>/dev/null; then echo "xterm"
    elif [[ "$OSTYPE" == "darwin"* ]]; then echo "macos"
    else echo "none"; fi
}
TERMINAL=$(detect_terminal)

run_in_term() {
    local title="$1" cmd="$2"
    case "$TERMINAL" in
        cosmic)   cosmic-term -e bash -c "$cmd 2>/dev/null; echo; echo '✅ Завершено. Нажмите Enter.'; read" & ;;
        gnome)    gnome-terminal --title="$title" -- bash -c "$cmd; exec bash" & ;;
        konsole)  konsole --new-tab --title "$title" -e bash -c "$cmd; exec bash" & ;;
        alacritty) alacritty -t "$title" -e bash -c "$cmd; exec bash" & ;;
        kitty)    kitty -t "$title" -- bash -c "$cmd; exec bash" & ;;
        xterm)    xterm -title="$title" -e bash -c "$cmd; exec bash" & ;;
        macos)    osascript -e "tell application \"Terminal\" to do script \"$cmd\"" & ;;
        *)        echo -e "${RED}❌ Терминал не найден. Запустите вручную:${NC}\n   $cmd\n" ;;
    esac
}

run_in_term " Backend - API" "cd '$PYTHON_DIR' && source venv/bin/activate && python api.py"
sleep 2
run_in_term "🌐 Frontend - VitePress" "cd '$SITE_DIR' && npm run dev"

if [ -f "$PROJECT_DIR/webhook-listener.py" ]; then
    sleep 1
    run_in_term "📡 CI/CD Webhook" "cd '$PROJECT_DIR' && source venv/bin/activate && python webhook-listener.py"
fi

echo -e "\n${GREEN}========================================================"
echo -e " ✅ ГОТОВО! Откройте: http://localhost:5173"
echo -e " 💡 Чтобы остановить: закройте окна или используйте stop.sh"
echo -e "========================================================${NC}"