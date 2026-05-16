#!/usr/bin/env python3
import requests, json, os, sys
from pathlib import Path
from typing import Union, Generator

OLLAMA_URL = "http://127.0.0.1:11434"
QDRANT_URL = "http://127.0.0.1:6333"
COLLECTION_NAME = "my_kb_local"

LLM_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
EMBEDDING_MODEL = "nomic-embed-text"
TOP_K = 5
MIN_SCORE = 0.2

LLM_OPTIONS = {
    "num_ctx": 2048,
    "num_gpu": 999,
    "num_thread": 8,
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

def _build_prompt(context: str, question: str) -> str:
    return f"""Ты — эксперт по технической документации. Отвечай ТОЛЬКО на основе контекста.

ПРАВИЛА:
1. Если ответа нет в контексте — напиши: "В базе знаний нет информации".
2. Не выдумывай факты.
3. Отвечай кратко, по делу, на русском.
4. Указывай статью из которой берешь информации в конце сообщения

КОНТЕКСТ:
{context}

ВОПРОС: {question}

ОТВЕТ:"""

def _get_context(question: str) -> tuple[bool, str]:
    """Возвращает (успех, контекст или ошибка)"""
    try:
        # 1. Эмбеддинг
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

        if not results:
            return False, "❌ В базе знаний не найдено информации по вашему вопросу."

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
            return False, "❌ Не удалось извлечь текст из найденных документов."
        
        return True, context

    except requests.exceptions.ConnectionError:
        return False, "❌ Не удалось соединиться с сервером. Проверьте Ollama и Qdrant."
    except Exception as e:
        return False, f"❌ Произошла ошибка: {str(e)}"

def _stream_answer_gen(prompt: str) -> Generator[str, None, None]:
    """🔥 Генератор: выдаёт чанки по мере генерации"""
    try:
        with requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": LLM_MODEL, "prompt": prompt, "stream": True, "options": LLM_OPTIONS},
            timeout=180,
            stream=True
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    if token:
                        yield token
                    if chunk.get("done", False):
                        break
    except Exception as e:
        yield f"\n❌ Ошибка стриминга: {e}"

def _get_answer_sync(prompt: str) -> str:
    """🔹 Синхронный ответ: ждёт полной генерации"""
    llm_resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": LLM_MODEL, "prompt": prompt, "stream": False, "options": LLM_OPTIONS},
        timeout=180
    )
    llm_resp.raise_for_status()
    return llm_resp.json().get("response", "").strip()

def get_answer(question: str, stream: bool = False) -> Union[str, Generator[str, None, None]]:
    """
    Получает ответ от LLM.
    
    Если stream=True — возвращает ГЕНЕРАТОР чанков.
    Если stream=False — возвращает полный ответ строкой.
    """
    # 🔥 1. Сначала получаем контекст (общая логика)
    success, result = _get_context(question)
    
    if not success:
        # 🔥 Возвращаем ошибку в правильном формате
        return (msg for msg in [result]) if stream else result
    
    # 🔥 2. Формируем промпт
    prompt = _build_prompt(result, question)
    
    # 🔥 3. Возвращаем в нужном формате (ЧЁТКОЕ РАЗДЕЛЕНИЕ!)
    if stream:
        return _stream_answer_gen(prompt)  # ✅ Генератор
    else:
        return _get_answer_sync(prompt)     # ✅ Строка

# === Тестовый запуск ===
if __name__ == "__main__":
    print(f"🤖 RAG Чат | Модель: {LLM_MODEL}")
    print("-" * 70)
    while True:
        try:
            q = input("\n❓ Вопрос: ").strip()
            if q.lower() in ("exit", "quit", "выход", "q"): 
                print("👋 До свидания!"); break
            if not q: continue
            
            # Тест стриминга в консоли
            print("🤔 Думаю...", end=" ", flush=True)
            result = get_answer(q, stream=True)
            
            if hasattr(result, '__iter__') and not isinstance(result, str):
                for chunk in result:
                    print(chunk, end="", flush=True)
            else:
                print(result, end="", flush=True)
            
            print("\n" + "-" * 70)
        except KeyboardInterrupt:
            print("\n👋 Выход"); break