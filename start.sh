#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$PROJECT_DIR/rag/knowledge-base"
SITE_DIR="$PROJECT_DIR/site"

# 🤖 Модель + оптимизация под 8 ГБ VRAM
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5:7b}"

echo -e "${GREEN} Запуск Knowledge Base...${NC}\n"

# 1️⃣ Сервисы + модель
echo -e "${YELLOW}📦 Qdrant...${NC}"
docker start qdrant 2>/dev/null || docker run -d --name qdrant -p 6333:6333 qdrant/qdrant

echo -e "${YELLOW}🤖 Ollama + модель ($OLLAMA_MODEL)...${NC}"
if ! curl -s http://localhost:11434 &>/dev/null; then
    echo -e "   ${RED}⚠️ Ollama не отвечает. Запустите: ollama serve${NC}"
else
    if ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
        echo -e "   ✅ Модель уже установлена"
    else
        echo -e "   ⬇️ Скачиваем $OLLAMA_MODEL (~4.2 ГБ VRAM)... Ожидайте."
        ollama pull "$OLLAMA_MODEL"
        echo -e "   ✅ Готово"
    fi
fi

# 2️⃣ Python
echo -e "${YELLOW} Python...${NC}"
cd "$PYTHON_DIR" || exit
[ ! -d "venv" ] && python3 -m venv venv
source venv/bin/activate
pip install -q flask flask-cors requests llama-index llama-index-core llama-index-embeddings-ollama llama-index-llms-ollama llama-index-vector-stores-qdrant==0.1.4 "numpy<2" python-dotenv pypdf 2>/dev/null

# 3️⃣ Данные
echo -e "${YELLOW} Синхронизация...${NC}"
cd "$SITE_DIR" || exit
python3 sync.py

echo -e "${YELLOW}🧠 Индексация...${NC}"
cd "$PYTHON_DIR" || exit
python3 ingest.py

# 4️⃣ Запуск в cosmic-term
echo -e "${GREEN}✨ Запуск серверов...${NC}\n"

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
    local title="$1" 
    local cmd="$2"
    
    case "$TERMINAL" in
        cosmic)
            cosmic-term -e bash -ic "$cmd; echo; echo '✅ Завершено. Нажмите Enter.'; read" & 
            ;;
        gnome)    gnome-terminal --title="$title" -- bash -ic "$cmd; exec bash" & ;;
        konsole)  konsole --new-tab --title "$title" -e bash -ic "$cmd; exec bash" & ;;
        alacritty) alacritty -t "$title" -e bash -ic "$cmd; exec bash" & ;;
        kitty)    kitty -t "$title" -- bash -ic "$cmd; exec bash" & ;;
        xterm)    xterm -title "$title" -e bash -ic "$cmd; exec bash" & ;;
        macos)    osascript -e "tell application \"Terminal\" to do script \"$cmd\"" & ;;
        *)        echo -e "${RED}❌ Терминал не найден. Запустите вручную:${NC}\n   $cmd\n" ;;
    esac
}

run_in_term "🔙 API" "cd '$PYTHON_DIR' && source venv/bin/activate && python api.py"
sleep 1
# СТАЛО ✅ — Сборка + деплой статики
echo -e "${YELLOW}📦 Сборка фронтенда...${NC}"
cd "$SITE_DIR" || exit
npm run build

# Копируем билд на VPS (замените путь на ваш)
echo -e "${YELLOW}🚀 Деплой на VPS...${NC}"
rsync -avz --delete docs/.vitepress/dist/ root@86.110.194.68:/var/www/swinki.ru/dist/

echo -e "${GREEN}✅ Фронтенд собран и задеплоен${NC}"
echo -e "${GREEN}✅ Сборка завершена. Файлы в: $SITE_DIR/docs/.vitepress/dist${NC}"
if [ -f "$PROJECT_DIR/webhook-listener.py" ]; then
    sleep 1
    run_in_term "📡 Webhook" "cd '$PROJECT_DIR' && source venv/bin/activate && python webhook-listener.py"
else
    echo -e "${YELLOW}⚠️ webhook-listener.py не найден. CI/CD не активен.${NC}"
fi

echo -e "\n${GREEN}✅ Готово! Откройте: http://localhost:5173${NC}"
echo -e "${YELLOW}💡 Чтобы остановить: закройте вкладки терминала${NC}"