#!/usr/bin/env python3

import http.server, subprocess, json, os, hashlib, hmac, sys, logging, threading
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# 🔐 Настройки
SECRET = os.getenv("WEBHOOK_SECRET", "").encode()
if not SECRET:
    print("❌ WEBHOOK_SECRET не задан в .env!", file=sys.stderr)
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.resolve()
UPDATE_SCRIPT = PROJECT_ROOT / "scripts" / "update.sh"
PORT = int(os.getenv("WEBHOOK_PORT", "25000"))

# 📝 Логирование
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "webhook.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def verify_signature(payload: bytes, signature: str) -> bool:
    if not signature or not signature.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(SECRET, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)

def run_update_async():
    """Запускает update.sh в отдельном потоке"""
    try:
        logger.info("🔄 [ASYNC] Запуск update.sh...")
        result = subprocess.run(
            [str(UPDATE_SCRIPT)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
            timeout=1800
        )
        if result.returncode == 0:
            logger.info("✅ [ASYNC] Обновление завершено!")
        else:
            logger.error(f"❌ [ASYNC] Ошибка (код {result.returncode}): {result.stderr[:500]}")
    except Exception as e:
        logger.error(f"❌ [ASYNC] Критическая ошибка: {e}")

class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    
    def log_message(self, *args): pass  # Отключаем спам
    
    def _send(self, code: int, body: dict):
        response = json.dumps(body).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(response)
        self.wfile.flush()
    
    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "ok"})
        else:
            self._send(404, {"error": "not found"})
    
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            payload = self.rfile.read(length)
            signature = self.headers.get("X-Hub-Signature-256", "")
            
            if not verify_signature(payload, signature):
                logger.warning(f"❌ Invalid signature from {self.client_address[0]}")
                self._send(403, {"error": "invalid signature"})
                return
            
            data = json.loads(payload)
            if data.get("ref") != "refs/heads/main":
                self._send(200, {"status": "ignored"})
                return
            
            logger.info(f"🔄 Push в main от {data.get('repository', {}).get('full_name', 'unknown')}")
            
            # 🔥 СРАЗУ отвечаем — до запуска update.sh!
            self._send(202, {"status": "accepted"})
            
            # 🔥 Потом запускаем обновление в фоне
            threading.Thread(target=run_update_async, daemon=True).start()
            
        except Exception as e:
            logger.error(f"❌ Handler error: {e}", exc_info=True)
            try:
                self._send(500, {"error": "internal"})
            except:
                pass

def main():
    if not UPDATE_SCRIPT.exists():
        logger.error(f"❌ Скрипт не найден: {UPDATE_SCRIPT}")
        sys.exit(1)
    
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    logger.info(f"🎣 Webhook listener запущен на порту {PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("👋 Остановка...")
        server.shutdown()

if __name__ == "__main__":
    main()