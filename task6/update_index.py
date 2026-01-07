import os
import json
import hashlib
import logging
import re
import inspect
from pathlib import Path
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Monkey patch for pymorphy2 compatibility with Python 3.11
if not hasattr(inspect, 'getargspec'):
    def getargspec(func):
        full = inspect.getfullargspec(func)
        return (full.args, full.varargs, full.varkw, full.defaults)
    inspect.getargspec = getargspec

import pymorphy2

# Настройка логирования
logging.basicConfig(
    filename='update_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# Конфигурация
KNOWLEDGE_BASE_DIR = Path('knowledge_base')
CHROMA_DB_DIR = Path('chroma_db')
COLLECTION_NAME = 'quantumforge_hp_world'
EMBEDDING_MODEL_NAME = 'BAAI/bge-m3'
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TERMS_MAP_FILE = Path('terms_map.json')
STATE_FILE = Path('file_state.json')

# Загрузка словаря замен и построение форм
def load_terms_and_build_forms():
    if TERMS_MAP_FILE.exists():
        with open(TERMS_MAP_FILE, 'r', encoding='utf-8') as f:
            terms_map = json.load(f)
    else:
        logging.warning('Файл terms_map.json не найден. Замены терминов не будут применены.')
        return {}

    morph = pymorphy2.MorphAnalyzer()
    forms_map = {}
    for old_term, new_term in terms_map.items():
        # Добавляем базовую форму полного термина
        forms_map[old_term] = new_term
        # Разбираем старый термин
        old_parsed = morph.parse(old_term)[0]
        new_parsed = morph.parse(new_term)[0]
        old_lexeme = old_parsed.lexeme
        new_lexeme = new_parsed.lexeme
        for old_form, new_form in zip(old_lexeme, new_lexeme):
            forms_map[old_form.word] = new_form.word

        # Также добавляем отдельные слова, если термин составной
        old_words = old_term.split()
        new_words = new_term.split()
        if len(old_words) > 1:
            for ow, nw in zip(old_words, new_words):
                forms_map[ow] = nw
                # И их формы
                ow_parsed = morph.parse(ow)[0]
                nw_parsed = morph.parse(nw)[0]
                ow_lexeme = ow_parsed.lexeme
                nw_lexeme = nw_parsed.lexeme
                for owf, nwf in zip(ow_lexeme, nw_lexeme):
                    forms_map[owf.word] = nwf.word
    return forms_map

# Замена терминов в тексте
def replace_terms(text, forms_map):
    replaced_text = text
    for old_form, new_form in forms_map.items():
        replaced_text = re.sub(r'\b' + re.escape(old_form) + r'\b', new_form, replaced_text)
    return replaced_text

# Хэш файла для определения изменений
def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

# Работа с состоянием файлов
def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# Основная функция обновления
def update_index():
    start_time = datetime.now()
    logging.info('=== Запуск обновления индекса ===')

    try:
        forms_map = load_terms_and_build_forms()
        previous_state = load_state()
        current_state = {}
        new_or_changed_files = []

        # Сканирование папки knowledge_base
        if not KNOWLEDGE_BASE_DIR.exists():
            logging.error(f'Папка {KNOWLEDGE_BASE_DIR} не существует!')
            return 0, 1

        for file_path in KNOWLEDGE_BASE_DIR.glob('*.txt'):
            current_hash = get_file_hash(file_path)
            file_key = str(file_path.name)

            if previous_state.get(file_key, {}).get('hash') != current_hash:
                new_or_changed_files.append(file_path)
                logging.info(f'Новый или изменённый файл: {file_path.name}')

            current_state[file_key] = {'hash': current_hash, 'mtime': os.path.getmtime(file_path)}

        if not new_or_changed_files:
            logging.info('Нет новых или изменённых файлов. Обновление не требуется.')
            print(f"Index update skipped at {datetime.now().date()} — no changes detected.")
            return 0, 0

        # Подготовка чанков
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " "]
        )

        model = SentenceTransformer(EMBEDDING_MODEL_NAME)

        chunks_to_add = []
        for file_path in new_or_changed_files:
            raw_text = file_path.read_text(encoding='utf-8')
            text = replace_terms(raw_text, forms_map)
            split_texts = splitter.split_text(text)

            for i, chunk_text in enumerate(split_texts):
                embedding = model.encode(chunk_text, normalize_embeddings=True).tolist()
                chunks_to_add.append({
                    'id': f"{file_path.stem}_chunk_{i}",
                    'content': chunk_text,
                    'embedding': embedding,
                    'metadata': {
                        'source': file_path.name,
                        'title': file_path.stem.replace('_', ' ').title(),
                        'chunk_index': i,
                        'total_chunks': len(split_texts)
                    }
                })

        # Обновление ChromaDB
        client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
        embedding_func = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_func,
            metadata={"hnsw:space": "cosine"}
        )

        # Удаление старых чанков для изменённых файлов
        deleted_count = 0
        for file_path in new_or_changed_files:
            prefix = f"{file_path.stem}_chunk_"
            existing_ids = [id for id in collection.get()['ids'] if id.startswith(prefix)]
            if existing_ids:
                collection.delete(ids=existing_ids)
                deleted_count += len(existing_ids)
                logging.info(f'Удалено {len(existing_ids)} старых чанков для файла {file_path.name}')

        # Добавление новых чанков
        if chunks_to_add:
            collection.add(
                ids=[c['id'] for c in chunks_to_add],
                documents=[c['content'] for c in chunks_to_add],
                embeddings=[c['embedding'] for c in chunks_to_add],
                metadatas=[c['metadata'] for c in chunks_to_add]
            )
            logging.info(f'Добавлено {len(chunks_to_add)} новых чанков')

        # Сохранение состояния
        save_state(current_state)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        total_docs = collection.count()
        logging.info(f'Обновление завершено успешно. Добавлено чанков: {len(chunks_to_add)}, '
                     f'удалено: {deleted_count}, итого в индексе: {total_docs}. Время: {duration:.2f} сек.')

        print(f"Index updated at {datetime.now().date()}, {len(chunks_to_add)} chunks added, "
              f"{deleted_count} removed, {total_docs} total, 0 errors.")

        return len(chunks_to_add), 0

    except Exception as e:
        logging.error(f'Критическая ошибка при обновлении индекса: {str(e)}', exc_info=True)
        print(f"Index update failed at {datetime.now().date()} with error: {str(e)}")
        return 0, 1

if __name__ == '__main__':
    new_chunks, errors = update_index()
    exit(errors)  # Для cron: код возврата 0 — успех, 1 — ошибка
