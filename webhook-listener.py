#!/usr/bin/env python3
import http.server, subprocess, json, os, hashlib, hmac, sys, logging
from pathlib import Path

# 🔐 Настройки
SECRET = os.getenv("WEBHOOK_SECRET", "change_me").encode()
PROJECT_DIR = Path(__file__).parent.resolve()
PORT = int(os.getenv("WEBHOOK_PORT", "25000"))

# 📝 Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_DIR / "webhook.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args): pass  # Отключаем стандартный спам
    
    def do_POST(self):
        try:
            # Проверка подписи
            signature = self.headers.get('X-Hub-Signature-256', '')
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len)
            
            expected = 'sha256=' + hmac.new(SECRET, body, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                logger.warning(f"❌ Invalid signature from {self.client_address[0]}")
                self.send_response(403); self.end_headers()
                return
            
            # Парсинг события
            event = self.headers.get('X-GitHub-Event')
            if event != 'push':
                self.send_response(200); self.end_headers()
                return
                
            payload = json.loads(body)
            branch = payload.get('ref', '').split('/')[-1]
            
            if branch == 'main':
                logger.info(f"🔄 Push в main от {payload.get('repository', {}).get('full_name')}")
                self.run_update()
            else:
                logger.info(f"⏭ Пропущен пуш в ветку {branch}")
            
            self.send_response(200); self.end_headers()
            
        except Exception as e:
            logger.error(f"❌ Webhook error: {e}")
            self.send_response(500); self.end_headers()
    
    def run_update(self):
        """Выполняет обновление: git pull → sync → ingest"""
        try:
            os.chdir(PROJECT_DIR)
            
            # 1. Git pull
            logger.info("📥 git pull...")
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                capture_output=True, text=True, timeout=120, cwd=PROJECT_DIR
            )
            if result.returncode != 0:
                logger.error(f"❌ Git pull failed: {result.stderr}")
                return
            logger.info(f"✅ Git: {result.stdout.strip()}")
            
            # 2. Синхронизация статей
            logger.info("🔄 Синхронизация...")
            result = subprocess.run(
                [sys.executable, 'site/sync.py'],
                capture_output=True, text=True, timeout=300, cwd=PROJECT_DIR
            )
            if result.returncode != 0:
                logger.error(f"❌ Sync failed: {result.stderr}")
                return
            
            # 3. Переиндексация
            logger.info("🧠 Индексация...")
            result = subprocess.run(
                [sys.executable, 'rag/knowledge-base/ingest.py'],
                capture_output=True, text=True, timeout=900, cwd=PROJECT_DIR
            )
            if result.returncode != 0:
                logger.error(f"❌ Ingest failed: {result.stderr}")
                return
            
            logger.info("✅ Обновление завершено!")
            
        except subprocess.TimeoutExpired as e:
            logger.error(f"⏱ Timeout: {e}")
        except Exception as e:
            logger.error(f"❌ Update error: {e}")

if __name__ == '__main__':
    logger.info(f"🎣 Webhook listener started on port {PORT}")
    logger.info(f"   Project: {PROJECT_DIR}")
    http.server.HTTPServer(('', PORT), Handler).serve_forever()