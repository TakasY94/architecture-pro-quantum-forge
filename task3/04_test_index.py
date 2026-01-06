# 04_test_index.py
import chromadb
from config import CHROMA_DB_DIR, COLLECTION_NAME, TEST_QUERIES

def test_search():
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    collection = client.get_collection(name=COLLECTION_NAME)

    print("Тестируем поиск по индексу:\n")

    for query in TEST_QUERIES:
        print(f"Запрос: {query}")
        results = collection.query(
            query_texts=[query],
            n_results=4,
            include=["documents", "metadatas", "distances"]
        )

        print("Топ-результаты:")
        for i in range(len(results["documents"][0])):
            doc = results["documents"][0][i]
            meta = results["metadatas"][0][i]
            dist = results["distances"][0][i]
            print(f"  [{i+1}] {meta['title']} (chunk {meta['chunk_index']+1}/{meta['total_chunks']}) — расстояние: {dist:.4f}")
            doc_preview = doc[:300].replace('\n', ' ')
            print(f"      {doc_preview}...\n")
        print("-" * 80)

if __name__ == "__main__":
    test_search()
