# 03_build_chroma_index.py
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import json
from config import CHROMA_DB_DIR, COLLECTION_NAME, EMBEDDING_MODEL_NAME

def build_index():
    print("Инициализируем ChromaDB клиент...")
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))

    print(f"Создаём/получаем коллекцию: {COLLECTION_NAME}")
    embedding_function = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"}
    )

    # Загружаем чанки с предвычисленными эмбеддингами
    with open("chunks_with_embeddings.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Добавляем {len(chunks)} документов в индекс...")

    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["content"] for c in chunks],
        embeddings=[c["embedding"] for c in chunks],  # используем уже посчитанные
        metadatas=[{
            "source": c["source"],
            "title": c["title"],
            "chunk_index": c["chunk_index"],
            "total_chunks": c["total_chunks"]
        } for c in chunks]
    )

    print(f"Индекс успешно создан! Всего документов в коллекции: {collection.count()}")

if __name__ == "__main__":
    build_index()