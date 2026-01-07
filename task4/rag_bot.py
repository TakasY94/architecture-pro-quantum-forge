# rag_bot.py
from utils import generate_answer

def main():
    print("🚀 RAG-Бот на GigaChat по вымышленной магической вселенной запущен!")
    print("Задавай вопросы на русском языке. Для выхода введи 'exit' или 'quit'.\n")

    while True:
        try:
            query = input("Ваш вопрос: ").strip()
            if query.lower() in {"exit", "quit", "выход"}:
                print("До свидания!")
                break
            if not query:
                continue

            answer = generate_answer(query)
            print(f"\n{answer}\n")
            print("-" * 80)

        except KeyboardInterrupt:
            print("\n\nЗавершение работы.")
            break
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()