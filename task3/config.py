# config.py
from pathlib import Path

# Путь к базе знаний
KNOWLEDGE_BASE_DIR = Path("../task2/knowledge_base/")

# Путь к ChromaDB
CHROMA_DB_DIR = Path("chroma_db")

# Название коллекции
COLLECTION_NAME = "quantumforge_hp_world"

# Параметры чанкинга
CHUNK_SIZE = 1000      # символов (~200-300 слов)
CHUNK_OVERLAP = 200

# Выбранная модель эмбеддингов
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"   # multilingual, топ на MTEB 2025, размер 1024

# Параметры поиска при тесте
TEST_QUERIES = [
    "Кто такой Гарольд Поттерман?",
    "Расскажи про Львиный дом",
    "Расскажи про Азкабан",
    "Кто директор школы Догвартс"
]