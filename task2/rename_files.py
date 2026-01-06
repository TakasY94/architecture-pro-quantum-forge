import json
import os
import shutil

# Загрузка словаря терминов
with open('terms_map.json', 'r', encoding='utf-8') as f:
    terms_map = json.load(f)

# Папка
output_dir = 'knowledge_base'

# Создание словаря для переименования файлов
file_rename_map = {}
for old_term, new_term in terms_map.items():
    # Предполагаем, что файлы названы по персонажам/терминам
    old_filename = old_term.replace(' ', '_') + '.txt'
    new_filename = new_term.replace(' ', '_') + '.txt'
    file_rename_map[old_filename] = new_filename

# Переименование файлов
for old_filename, new_filename in file_rename_map.items():
    old_filepath = os.path.join(output_dir, old_filename)
    new_filepath = os.path.join(output_dir, new_filename)
    if os.path.exists(old_filepath):
        os.rename(old_filepath, new_filepath)
        print(f"Переименован: {old_filename} -> {new_filename}")
    else:
        print(f"Файл не найден: {old_filename}")

print("Переименование файлов завершено.")
