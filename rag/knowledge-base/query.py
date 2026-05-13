#!/usr/bin/env python3
import requests, json, os, sys
from pathlib import Path

OLLAMA_URL = "http://127.0.0.1:11434"
QDRANT_URL = "http://127.0.0.1:6333"
COLLECTION_NAME = "my_kb_local"

# 🤖 Модель + оптимизация под 8 ГБ
LLM_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
EMBEDDING_MODEL = "nomic-embed-text"
TOP_K = 5
MIN_SCORE = 0.2

# ⚙️ Параметры генерации (ОПТИМИЗИРОВАНО для скорости)
LLM_OPTIONS = {
    "num_ctx": 2048,      # ↓ Уменьшаем контекст (экономит ~1 ГБ VRAM)
    "num_gpu": 999,       # 🔒 Принудительно держим ВСЕ слои на GPU
    "num_thread": 8,      #  Потоки CPU для фоновых задач
    "temperature": 0.2,
    "top_p": 0.9,
    "repeat_penalty": 1.1,
    "stop": ["\n\nUser:", "ВОПРОС:", "КОНТЕКСТ:"]
}

def _extract_text(payload: dict) -> str:
    if payload.get("text"): return payload["text"]
    if "_node_content" in payload:
        try:
            node = json.loads(payload["_node_content"])
            if node.get("text"): return node["text"]
        except: pass
    parts = [str(v) for k, v in payload.items() 
             if k not in ("_node_content", "embedding") and isinstance(v, (str, int, float))]
    return " ".join(parts)[:2000]

def get_answer(question: str, stream: bool = True) -> str:
    """
    Получает ответ от LLM.
    Если stream=True — печатает ответ построчно в реальном времени.
    """
    try:
        print(f"🔍 Поиск: '{question}'")
        
        # 1. Эмбеддинг вопроса
        embed_resp = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBEDDING_MODEL, "input": [question]},
            timeout=30
        )
        embed_resp.raise_for_status()
        question_vector = embed_resp.json()["embeddings"][0]

        # 2. Поиск в Qdrant
        search_resp = requests.post(
            f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points/search",
            json={"vector": question_vector, "limit": TOP_K, "with_payload": True, "score_threshold": MIN_SCORE},
            timeout=30
        )
        search_resp.raise_for_status()
        results = search_resp.json()["result"]

        print(f"📄 Найдено {len(results)} фрагментов (score >= {MIN_SCORE})")
        if not results:
            return "❌ В базе знаний не найдено информации по вашему вопросу. Попробуйте сформулировать иначе."

        # 3. Формируем контекст
        context_parts = []
        for i, r in enumerate(results, 1):
            payload = r.get("payload", {})
            text = _extract_text(payload)
            score = r.get("score", 0)
            if text and len(text.strip()) > 20:
                context_parts.append(f"[{i}] (score: {score:.3f}) {text.strip()}")
        
        context = "\n\n".join(context_parts)
        if not context:
            return "❌ Не удалось извлечь текст из найденных документов."

        # 4. Промпт (оптимизирован для краткости)
        prompt = f"""Ты — эксперт по технической документации. Отвечай ТОЛЬКО на основе контекста.

ПРАВИЛА:
1. Если ответа нет в контексте — напиши: "В базе знаний нет информации".
2. Не выдумывай факты.
3. Отвечай кратко, по делу, на русском.

КОНТЕКСТ:
{context}

ВОПРОС: {question}

ОТВЕТ:"""

        # 5. Запрос к LLM
        if stream:
            return _stream_answer(prompt)
        else:
            return _get_answer_sync(prompt)

    except requests.exceptions.ConnectionError:
        return "❌ Не удалось соединиться с сервером. Проверьте Ollama и Qdrant."
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        return f"❌ Произошла ошибка: {str(e)}"

def _stream_answer(prompt: str) -> str:
    """Потоковый ответ — печатает по мере генерации"""
    answer_parts = []
    
    try:
        with requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": LLM_MODEL, "prompt": prompt, "stream": True, "options": LLM_OPTIONS},
            timeout=180,
            stream=True
        ) as resp:
            resp.raise_for_status()
            print("💡 ", end="", flush=True)  # Начало ответа
            
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    if token:
                        print(token, end="", flush=True)  # 🔥 Печатаем сразу!
                        answer_parts.append(token)
                    if chunk.get("done", False):
                        break
        print()  # Новая строка после ответа
        return "".join(answer_parts).strip()
        
    except Exception as e:
        print(f"\n❌ Ошибка стриминга: {e}")
        return _get_answer_sync(prompt)  # Фолбэк на синхронный режим

def _get_answer_sync(prompt: str) -> str:
    """Синхронный ответ — ждёт полной генерации (фолбэк)"""
    llm_resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": LLM_MODEL, "prompt": prompt, "stream": False, "options": LLM_OPTIONS},
        timeout=180
    )
    llm_resp.raise_for_status()
    return llm_resp.json().get("response", "").strip()

if __name__ == "__main__":
    print(f"🤖 RAG Чат | Модель: {LLM_MODEL} | Стриминг: ✅")
    print("-" * 70)
    while True:
        try:
            q = input("\n❓ Вопрос: ").strip()
            if q.lower() in ("exit", "quit", "выход", "q"): 
                print("👋 До свидания!"); break
            if not q: continue
            print("🤔 Думаю...", end=" ", flush=True)
            answer = get_answer(q, stream=True)  # 🔥 Включаем стриминг
            print("-" * 70)
        except KeyboardInterrupt:
            print("\n👋 Выход"); break