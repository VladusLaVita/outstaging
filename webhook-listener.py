#!/usr/bin/env python3
"""
Webhook listener для автоматического обновления при git push.
Принимает подписанные запросы от GitHub Actions и запускает update.sh
"""
import http.server, subprocess, json, os, hashlib, hmac, sys, logging, socket
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv(Path(__file__).parent / ".env")

# 🔐 Настройки
SECRET = os.getenv("WEBHOOK_SECRET", "").encode()
if not SECRET:
    print("❌ WEBHOOK_SECRET не задан в .env!")
    sys.exit(1)

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", Path(__file__).parent.resolve()))
UPDATE_SCRIPT = PROJECT_ROOT / "scripts" / "update.sh"
PORT = int(os.getenv("WEBHOOK_PORT", "25000"))

# 📝 Логирование
LOG_FILE = PROJECT_ROOT / "webhook.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def verify_signature(payload: bytes, signature: str) -> bool:
    """Проверяет HMAC-SHA256 подпись от GitHub"""
    if not signature.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(SECRET, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)

def run_update():
    """Запускает скрипт обновления в фоне"""
    try:
        logger.info("🔄 Запуск update.sh...")
        # Запускаем в фоне, чтобы не блокировать вебхук
        proc = subprocess.Popen(
            [str(UPDATE_SCRIPT)],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env={**os.environ, "PYTHONUNBUFFERED": "1"}
        )
        # Читаем вывод в реальном времени
        for line in proc.stdout:
            logger.info(f"   {line.strip()}")
        proc.wait()
        if proc.returncode == 0:
            logger.info("✅ Обновление завершено успешно!")
            notify_telegram("✅ KB обновлён", "Все статьи синхронизированы и проиндексированы.")
        else:
            logger.error(f"❌ Обновление завершилось с кодом {proc.returncode}")
            notify_telegram("❌ Ошибка обновления", f"Код возврата: {proc.returncode}")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска update.sh: {e}")
        notify_telegram("❌ Ошибка CI/CD", str(e))

def notify_telegram(title: str, message: str):
    """Отправляет уведомление в Telegram (если настроено)"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return  # Не настроено — молча пропускаем
    try:
        import requests
        text = f"*{title}*\n\n{message}"
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=10
        )
    except Exception as e:
        logger.warning(f"⚠️ Не удалось отправить уведомление в Telegram: {e}")

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args): pass  # Отключаем стандартный спам
    
    def do_GET(self):
        """Health check endpoint"""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Обработка вебхука от GitHub"""
        try:
            # Проверка подписи
            signature = self.headers.get("X-Hub-Signature-256", "")
            content_len = int(self.headers.get("Content-Length", 0))
            payload = self.rfile.read(content_len)
            
            if not verify_signature(payload, signature):
                logger.warning(f"❌ Invalid signature from {self.client_address[0]}")
                self.send_response(403)
                self.end_headers()
                return
            
            # Парсинг события
            event = self.headers.get("X-GitHub-Event")
            if event != "push":
                self.send_response(200)  # Игнорируем другие события
                self.end_headers()
                return
            
            data = json.loads(payload)
            ref = data.get("ref", "")
            repo = data.get("repository", {}).get("full_name", "unknown")
            
            if ref != "refs/heads/main":
                logger.info(f"⏭ Пропущен пуш в {ref} от {repo}")
                self.send_response(200)
                self.end_headers()
                return
            
            logger.info(f"🔄 Получен push в main от {repo}")
            
            # Запускаем обновление в отдельном потоке
            import threading
            threading.Thread(target=run_update, daemon=True).start()
            
            self.send_response(202)  # Accepted
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "updating"}).encode())
            
        except Exception as e:
            logger.error(f"❌ Webhook error: {e}")
            self.send_response(500)
            self.end_headers()

def main():
    # Проверка, что скрипт обновления существует
    if not UPDATE_SCRIPT.exists():
        logger.error(f"❌ Скрипт обновления не найден: {UPDATE_SCRIPT}")
        sys.exit(1)
    
    # Проверка порта
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", PORT))
        except OSError:
            logger.error(f"❌ Порт {PORT} занят! Завершите старый процесс или смените порт.")
            sys.exit(1)
    
    logger.info(f"🎣 Webhook listener запущен на порту {PORT}")
    logger.info(f"   Проект: {PROJECT_ROOT}")
    logger.info(f"   Скрипт обновления: {UPDATE_SCRIPT}")
    
    server = http.server.HTTPServer(("0.0.0.0", PORT), WebhookHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("👋 Остановка...")
        server.shutdown()

if __name__ == "__main__":
    main()