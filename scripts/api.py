#!/usr/bin/env python3
"""
Flask API для Knowledge Base — с ПОЛНОЦЕННЫМ стримингом.
📍 Расположение: scripts/api.py
🚀 Запускается через Gunicorn (Linux) или Waitress (Windows)
"""
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from pathlib import Path
import sys, os, time, logging, json
from dotenv import load_dotenv

# 🔗 Пути: scripts/ -> корень проекта
SCRIPTS_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPTS_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 🔧 Добавляем scripts/ в путь для импорта локальных модулей
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# 🔐 Загружаем .env из корня
load_dotenv(PROJECT_ROOT / ".env")

# 📝 Логирование в файл + консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "api.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 🔥 Импорт query.py
try:
    from query import get_answer
except ImportError as e:
    logger.error(f"❌ Не удалось импортировать get_answer: {e}")
    logger.error("💡 Убедитесь, что query.py находится в папке scripts/")
    sys.exit(1)

# 🚀 Создание Flask приложения
app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173", 
    "https://swinki.ru",
    "https://www.swinki.ru"
])

# === Эндпоинты ===

@app.route('/health', methods=['GET'])
def health():
    """Health check для мониторинга"""
    return jsonify({"status": "ok", "service": "kb-api"}), 200

@app.route('/api/ask', methods=['POST'])
def ask():
    """
    Основной эндпоинт для вопросов.
    Поддерживает стриминг через ?stream=true (SSE format).
    """
    start_time = time.time()
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type должен быть application/json"}), 400
            
        question = request.json.get('question', '').strip()
        if not question:
            return jsonify({"error": "Пустой вопрос"}), 400
        
        # 🔥 Поддержка стриминга через ?stream=true
        stream = request.args.get('stream', 'false').lower() == 'true'
        
        if stream:
            # 🔥 ГЕНЕРАТОР ДЛЯ СТРИМИНГА (SSE)
            def generate():
                try:
                    # Получаем генератор чанков из query.py
                    answer_gen = get_answer(question, stream=True)
                    
                    for chunk in answer_gen:
                        # Пропускаем пустые чанки
                        if not chunk or not chunk.strip():
                            continue
                            
                        # Формируем JSON для чанка
                        data = json.dumps({
                            "success": True,
                            "chunk": chunk,
                            "meta": {"time_sec": round(time.time() - start_time, 2)}
                        }, ensure_ascii=False)
                        
                        # 🔥 SSE-формат + 🔥 КОДИРОВКА В БАЙТЫ для Gunicorn
                        yield f"data: {data}\n\n".encode('utf-8')
                        
                except StopIteration:
                    pass
                except Exception as e:
                    logger.error(f"❌ Stream error: {e}")
                    error_data = json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)
                    yield f"data: {error_data}\n\n".encode('utf-8')
                finally:
                    # Сигнал конца потока (тоже в байтах!)
                    yield b"data: [DONE]\n\n"
            
            # 🔥 КРИТИЧНЫЕ ЗАГОЛОВКИ для стриминга
            return Response(
                generate(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache, no-store, no-transform',
                    'X-Accel-Buffering': 'no',
                    'Connection': 'keep-alive',
                    'Transfer-Encoding': 'chunked',
                },
                direct_passthrough=True
            )
        else:
            # 🔹 Синхронный ответ (как было)
            logger.info(f"📥 Вопрос: {question[:200]}...")
            answer = get_answer(question, stream=False)
            elapsed = time.time() - start_time
            logger.info(f"✅ Ответ за {elapsed:.2f}с | Длина: {len(answer)} симв.")
            return jsonify({
                "success": True, 
                "answer": answer, 
                "meta": {"time_sec": round(elapsed, 2)}
            })
            
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ API error ({elapsed:.2f}s): {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500

# Этот блок оставлен закомментированным только для экстренной отладки.
# if __name__ == '__main__':
#     logger.warning("⚠️  Запуск через Flask dev server — только для отладки!")
#     app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)