#!/usr/bin/env python3
import os, sys, logging
from pathlib import Path
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# 🔇 Отключаем шумные логи во время индексации (оставляем только ошибки)
logging.getLogger("llama_index").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("qdrant_client").setLevel(logging.WARNING)

# ✅ Наш логгер оставляем на INFO для важных сообщений
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_DIR = SCRIPT_DIR.parent.parent / "data"

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "my_kb_local"

# 🤖 Модели (оптимизировано под 8 ГБ VRAM)
EMBEDDING_MODEL = "nomic-embed-text"  # ~0.5 ГБ, быстро и качественно
LLM_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")  # ~4.2 ГБ

# ⚙️ Параметры
CHUNK_SIZE = 256
CHUNK_OVERLAP = 32
EMBED_BATCH_SIZE = 4  # ↓ уменьшено для экономии VRAM

def main():
    logger.info(f"📂 Загрузка документов из: {DATA_DIR}")
    if not DATA_DIR.exists():
        logger.error(f"❌ Папка не найдена! Запустите сначала: python site/sync.py")
        sys.exit(1)

    try:
        documents = SimpleDirectoryReader(DATA_DIR).load_data()
        logger.info(f"✅ Загружено {len(documents)} документов.")
    except Exception as e:
        logger.error(f"❌ Ошибка чтения: {e}")
        sys.exit(1)

    if not documents:
        logger.warning("⚠️ Документы не найдены.")
        return

    client = QdrantClient(QDRANT_URL)
    
    if client.collection_exists(COLLECTION_NAME):
        logger.info("🗑️ Очищаю старую коллекцию...")
        client.delete_collection(COLLECTION_NAME)
    
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=768 if "nomic" in EMBEDDING_MODEL else 1024, distance=Distance.COSINE)
    )
    logger.info(f"✅ Коллекция '{COLLECTION_NAME}' создана")

    # 🎯 Настройки моделей (оптимизация под 8 ГБ VRAM)
    Settings.embed_model = OllamaEmbedding(
        model_name=EMBEDDING_MODEL, 
        embed_batch_size=EMBED_BATCH_SIZE, 
        request_timeout=120.0
    )
    
    Settings.llm = Ollama(
        model=LLM_MODEL, 
        request_timeout=120.0,
        num_ctx=4096,        # ← Контекст: 4096 токенов
        num_gpu=1,           # ← Вся модель на GPU
        temperature=0.2,     # ← Меньше выдумок
        top_p=0.9            # ← Баланс креативности
    )

    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    logger.info(f"⚡ Индексация... (Чанк: {CHUNK_SIZE})")
    
    # 🔥 Индексация с ЧИСТЫМ прогресс-баром (без логов HTTP)
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context,
        transformations=[SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)],
        show_progress=True  # tqdm будет обновляться в одной строке
    )
    
    logger.info("🎉 Индексация завершена!")

if __name__ == "__main__":
    main()