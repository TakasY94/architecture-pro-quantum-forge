# 01_load_and_split.py
import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import KNOWLEDGE_BASE_DIR, CHUNK_SIZE, CHUNK_OVERLAP
import json
import tqdm

def load_and_split():
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " "]
    )

    chunks = []
    files = list(KNOWLEDGE_BASE_DIR.glob("*.txt"))

    print(f"Найдено {len(files)} файлов в knowledge_base/")

    for file_path in tqdm.tqdm(files, desc="Обработка документов"):
        text = file_path.read_text(encoding="utf-8")
        split_texts = splitter.split_text(text)

        for i, chunk_text in enumerate(split_texts):
            chunks.append({
                "id": f"{file_path.stem}_chunk_{i}",
                "content": chunk_text,
                "source": file_path.name,
                "title": file_path.stem.replace("_", " ").title(),
                "chunk_index": i,
                "total_chunks": len(split_texts)
            })

    # Сохраняем промежуточный результат
    output_path = Path("chunks.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"Создано {len(chunks)} чанков. Сохранено в {output_path}")

if __name__ == "__main__":
    load_and_split()