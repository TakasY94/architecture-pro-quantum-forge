# config.py
from pathlib import Path

# Путь к векторной базе
CHROMA_DB_PATH = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "quantumforge_hp_world"

EMBEDDING_MODEL = "BAAI/bge-m3"

# Параметры поиска
N_RESULTS = 5                    # количество чанков для контекста
RELEVANCE_THRESHOLD = 0.55       # cosine distance; выше — "не знаю"
# Параметры генерации GigaChat
MAX_TOKENS = 800
TEMPERATURE = 0.7
TOP_P = 0.95
