#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для оценки RAG-бота на основе золотых вопросов.
Загружает вопросы из golden_questions.json, задаёт их боту и анализирует результаты.
"""

import json
import sys
import os
from collections import defaultdict

# Добавляем путь к task4 для импорта utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'task4'))
from utils import generate_answer

def load_golden_questions(filepath: str):
    """Загрузить золотые вопросы из JSON файла."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def evaluate_response(response: str, expected_known: str, chunks_found: bool) -> dict:
    """
    Оценить ответ бота.
    Возвращает словарь с результатами анализа.
    """
    is_successful = len(response) > 50 and "Я не знаю" not in response

    if expected_known == "yes":
        # Для известных тем: должно быть успешно и найдены чанки
        correct = is_successful and chunks_found
        expected_behavior = "Успешный ответ с чанками"
    else:
        # Для неизвестных тем: не должно быть успешно или чанки не найдены
        correct = not is_successful or not chunks_found
        expected_behavior = "Ответ 'Я не знаю' или отсутствие чанков"

    return {
        "is_successful": is_successful,
        "chunks_found": chunks_found,
        "correct": correct,
        "expected_behavior": expected_behavior,
        "response_length": len(response)
    }

def main():
    questions_file = "golden_questions.json"

    if not os.path.exists(questions_file):
        print(f"Файл {questions_file} не найден.")
        return

    questions = load_golden_questions(questions_file)
    print(f"Загружено {len(questions)} вопросов для оценки.\n")

    results = []
    summary = defaultdict(int)

    for i, q in enumerate(questions, 1):
        question = q["question"]
        expected_known = q["expected_known"]

        print(f"{i}. Вопрос: {question}")
        print(f"   Ожидается известным: {expected_known}")

        try:
            # Отключаем вывод бота для чистоты логов
            import io
            from contextlib import redirect_stdout, redirect_stderr

            stdout_capture = io.StringIO()
            with redirect_stdout(stdout_capture), redirect_stderr(stdout_capture):
                answer = generate_answer(question)

            # Определяем, были ли найдены чанки (из ответа или из логов, но просто проверим)
            # Поскольку мы не можем легко получить chunks здесь, предположим на основе ответа
            chunks_found = "Я не знаю — в базе знаний" not in answer

            evaluation = evaluate_response(answer, expected_known, chunks_found)

            print(f"   Ответ: {answer[:100]}{'...' if len(answer) > 100 else ''}")
            print(f"   Оценка: {'✓ Правильно' if evaluation['correct'] else '✗ Неправильно'}")
            print(f"   Длина ответа: {evaluation['response_length']}")
            print(f"   Чанки найдены: {chunks_found}")
            print()

            results.append({
                "question": question,
                "expected_known": expected_known,
                "answer": answer,
                **evaluation
            })

            summary[expected_known] += 1
            if evaluation["correct"]:
                summary[f"{expected_known}_correct"] += 1

        except Exception as e:
            print(f"   Ошибка при обработке: {e}")
            results.append({
                "question": question,
                "expected_known": expected_known,
                "error": str(e)
            })

    # Вывод итогов
    print("=" * 60)
    print("ИТОГИ ОЦЕНКИ:")
    print("=" * 60)

    total_correct = 0
    total_questions = len(questions)

    for expected in ["yes", "no"]:
        if expected in summary:
            count = summary[expected]
            correct = summary.get(f"{expected}_correct", 0)
            accuracy = correct / count * 100 if count > 0 else 0
            print(f"{expected.upper()} вопросы: {correct}/{count} ({accuracy:.1f}%)")
            total_correct += correct

    overall_accuracy = total_correct / total_questions * 100 if total_questions > 0 else 0
    print(f"\nОБЩАЯ ТОЧНОСТЬ: {total_correct}/{total_questions} ({overall_accuracy:.1f}%)")

    # Сохранить результаты в файл
    output_file = "evaluation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nПодробные результаты сохранены в {output_file}")

if __name__ == "__main__":
    main()
