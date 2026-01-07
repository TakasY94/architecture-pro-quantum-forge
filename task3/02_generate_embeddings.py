# 02_generate_embeddings.py
from sentence_transformers import SentenceTransformer
import json
from tqdm import tqdm
from config import EMBEDDING_MODEL_NAME
from pathlib import Path

def generate_embeddings():
    print(f"Загружаем модель эмбеддингов: {EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    # Загружаем чанки
    with open("chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Генерируем эмбеддинги для {len(chunks)} чанков...")

    for chunk in tqdm(chunks, desc="Эмбеддинги"):
        embedding = model.encode(chunk["content"], normalize_embeddings=True)
        chunk["embedding"] = embedding.tolist()

    # Сохраняем с эмбеддингами
    output_path = Path("chunks_with_embeddings.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)

    print(f"Эмбеддинги сохранены в {output_path}")

if __name__ == "__main__":
    generate_embeddings()