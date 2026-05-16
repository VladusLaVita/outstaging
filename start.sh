#!/usr/bin/env bash
# 📍 НАХОДИТСЯ В КОРНЕ ПРОЕКТА
# ✅ Плоская структура: venv/, scripts/, data/, logs/ в корне
# 🔥 Исправлено: надёжная установка pip, безопасные пути, отладка

set -eo pipefail  # 🔥 Без -u, чтобы не ломались цвета

# 🎨 Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# 📁 Пути
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$PROJECT_DIR/scripts"
VENV_DIR="$PROJECT_DIR/venv"
SITE_DIR="$PROJECT_DIR/site"
LOG_DIR="$PROJECT_DIR/logs"
VPS="root@86.110.194.68"
SSH_KEY="$HOME/.ssh/kb_vps"

mkdir -p "$LOG_DIR"

# 📊 Прогресс-бар
TOTAL_STEPS=10
CURRENT_STEP=0
progress() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    local pct=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    local bar=""
    for ((i=0; i<20; i++)); do
        [[ $i -lt $((pct/5)) ]] && bar+="#" || bar+="-"
    done
    printf "\r${CYAN}[%s] %3d%% | %s${NC}" "$bar" "$pct" "$1"
}
log_ok() { echo -e "\n${GREEN}✅ $1${NC}"; }
log_warn() { echo -e "\n${YELLOW}⚠️  $1${NC}"; }
log_err() { echo -e "\n${RED}❌ $1${NC}"; }

# 🚇 Туннели
start_tunnel() {
    progress "Туннель..."
    pkill -f "ssh.*-R.*86\.110\.194\.68" 2>/dev/null || true
    sleep 1
    
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -R 0.0.0.0:8000:localhost:8000 -N -o ServerAliveInterval=30 "$VPS" >> "$LOG_DIR/tunnel_api.log" 2>&1 &
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -R 0.0.0.0:25000:localhost:25000 -N -o ServerAliveInterval=30 "$VPS" >> "$LOG_DIR/tunnel_wh.log" 2>&1 &
    
    # Ждём подключения
    for i in {1..15}; do
        if ssh -i "$SSH_KEY" "$VPS" "ss -tlnp 2>/dev/null | grep -q ':8000 '" 2>/dev/null && \
           ssh -i "$SSH_KEY" "$VPS" "ss -tlnp 2>/dev/null | grep -q ':25000 '" 2>/dev/null; then
            break
        fi
        sleep 1
    done
    
    ssh -i "$SSH_KEY" "$VPS" "ss -tlnp 2>/dev/null | grep -q ':8000 '" 2>/dev/null && log_ok "API-туннель" || log_warn "API-туннель"
    ssh -i "$SSH_KEY" "$VPS" "ss -tlnp 2>/dev/null | grep -q ':25000 '" 2>/dev/null && log_ok "Webhook-туннель" || log_warn "Webhook-туннель"
}

# 🖥️ Запуск сервиса в терминале
launch_service() {
    local title="$1" work_dir="$2" venv="$3" script="$4"
    local cmd="cd '$work_dir' && source '$venv' && exec python3 '$script'"
    
    if command -v gnome-terminal &>/dev/null; then
        gnome-terminal --title="$title" -- bash -ic "$cmd" &
    elif command -v cosmic-term &>/dev/null; then
        cosmic-term -e bash -ic "$cmd" &
    elif command -v konsole &>/dev/null; then
        konsole --new-tab -e bash -ic "$cmd" &
    else
        # Fallback: просто в фоне
        (bash -ic "$cmd") &
    fi
}

# 🧹 Очистка при выходе
cleanup() {
    echo -e "\n${YELLOW}🛑 Остановка...${NC}"
    if [[ -f "$PROJECT_DIR/stop.sh" ]]; then
        bash "$PROJECT_DIR/stop.sh" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

# 🚀 ГЛАВНЫЙ ЗАПУСК
echo -e "${CYAN}╔════════════════════════╗${NC}"
echo -e "${CYAN}║  🚀 Запуск KB          ║${NC}"
echo -e "${CYAN}╚════════════════════════╝${NC}"

# 0. Очистка портов
progress "Очистка..."
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 25000/tcp 2>/dev/null || true
sleep 1
log_ok "Порты очищены"

# 1. Туннели
start_tunnel

# 2. Qdrant
progress "Qdrant..."
if command -v docker &>/dev/null; then
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^qdrant$"; then
        log_ok "Qdrant запущен"
    else
        docker run -d --name qdrant -p 6333:6333 --restart unless-stopped qdrant/qdrant >/dev/null 2>&1
        sleep 2
        log_ok "Qdrant запущен"
    fi
else
    log_warn "Docker не найден"
fi

# 3. Ollama
progress "Ollama..."
if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
    log_ok "Ollama готов"
else
    log_warn "Ollama не отвечает"
fi

# 4. Python venv + зависимости (МАКСИМАЛЬНО НАДЁЖНО)
progress "Python..."

# Создаём venv если нет
if [[ ! -d "$VENV_DIR" ]] || [[ ! -x "$VENV_DIR/bin/python3" ]]; then
    log_warn "⚠️  venv не найден — создаю..."
    rm -rf "$VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

# 🔥 Прямые пути к python/pip (БЕЗ source!)
PYTHON="$VENV_DIR/bin/python3"
PIP="$VENV_DIR/bin/pip"
[[ ! -x "$PIP" ]] && PIP="$VENV_DIR/bin/pip3"

if [[ ! -x "$PYTHON" ]]; then
    log_err "❌ Python в venv не найден!"
    exit 1
fi

# Обновляем pip
"$PIP" install -q --upgrade pip setuptools wheel 2>/dev/null || true

# Устанавливаем зависимости (без скрытия ошибок!)
echo ""  # Новая строка для вывода pip
if "$PIP" install -q -r "$PROJECT_DIR/requirements.txt" 2>&1 | tee -a "$LOG_DIR/start.log"; then
    log_ok "Зависимости установлены"
else
    log_warn "⚠️  pip install завершён с ошибками — см. $LOG_DIR/start.log"
fi

# 5. Синхронизация статей (ПРОВЕРКА ПО КОДУ ВОЗВРАТА)
progress "Синхронизация..."
cd "$PROJECT_DIR"
if "$PYTHON" "$SCRIPTS_DIR/sync.py" >> "$LOG_DIR/start.log" 2>&1; then
    log_ok "Данные синхронизированы"
else
    log_warn "sync.py упал — см. $LOG_DIR/start.log"
fi

# 6. Индексация (аналогично)
progress "Индексация..."
cd "$PROJECT_DIR"
if "$PYTHON" "$SCRIPTS_DIR/ingest.py" >> "$LOG_DIR/start.log" 2>&1; then
    log_ok "База проиндексирована"
else
    log_warn "ingest.py упал — см. $LOG_DIR/start.log"
fi

# 7. Сборка фронтенда
progress "Сборка..."
cd "$SITE_DIR"
if npm run build --silent 2>&1 | tee -a "$LOG_DIR/start.log"; then
    log_ok "Build завершён"
else
    log_warn "npm build упал — см. $LOG_DIR/start.log"
fi

# 8. Деплой
progress "Деплой..."
cd "$SITE_DIR"
if rsync -avz --delete -q docs/.vitepress/dist/ "$VPS:/var/www/swinki.ru/dist/" 2>/dev/null; then
    log_ok "Фронтенд задеплоен"
else
    log_warn "rsync не удался"
fi

# 9. Запуск API (Gunicorn — в основном потоке для корректного Ctrl+C)
progress "Запуск API..."
echo ""

GUNCORN_CMD="cd '$SCRIPTS_DIR' && source '$VENV_DIR/bin/activate' && exec gunicorn \
  -w 1 -k gthread --threads 2 --timeout 300 --bind 0.0.0.0:8000 \
  --access-logfile '$LOG_DIR/gunicorn-access.log' \
  --error-logfile '$LOG_DIR/gunicorn-error.log' \
  --preload 'api:app'"

# 🔥 Запускаем в НОВОМ терминале (чтобы не блокировал основной скрипт)
if command -v gnome-terminal &>/dev/null; then
    gnome-terminal --title="🔙 API" -- bash -ic "$GUNCORN_CMD" &
elif command -v cosmic-term &>/dev/null; then
    cosmic-term -e bash -ic "$GUNCORN_CMD" &
elif command -v konsole &>/dev/null; then
    konsole --new-tab -e bash -ic "$GUNCORN_CMD" &
else
    # Fallback: просто в фоне, но с правильным обработчиком сигналов
    (bash -ic "$GUNCORN_CMD") &
fi

# Даем время на старт
sleep 2

# Проверка
if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
    log_ok "API запущен (Gunicorn)"
else
    log_warn "API не отвечает — проверьте $LOG_DIR/gunicorn-error.log"
fi

# 10. Запуск Webhook
progress "Запуск Webhook..."
if [[ -f "$SCRIPTS_DIR/webhook-listener.py" ]]; then
    launch_service "📡 Webhook" "$PROJECT_DIR" "$VENV_DIR/bin/activate" "$SCRIPTS_DIR/webhook-listener.py"
    log_ok "Webhook запущен"
else
    log_warn "webhook-listener.py не найден"
fi

# === 🎉 ФИНАЛ ===
echo -e "\n\n${GREEN}╔════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 Готово!            ║${NC}"
echo -e "${GREEN}╚════════════════════════╝${NC}"
echo -e "🌐 ${CYAN}https://swinki.ru${NC}"
echo -e "🤖 ${CYAN}http://localhost:8000${NC}"
echo -e "🎣 ${CYAN}http://localhost:25000${NC}"
echo -e "${YELLOW}💡 Закройте вкладки или нажмите ./stop.sh для остановки${NC}"

# Ждём фоновые процессы
wait 2>/dev/null || true