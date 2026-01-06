import json
import os
import re
import inspect

# Monkey patch for pymorphy2 compatibility with Python 3.11
if not hasattr(inspect, 'getargspec'):
    def getargspec(func):
        full = inspect.getfullargspec(func)
        return (full.args, full.varargs, full.varkw, full.defaults)
    inspect.getargspec = getargspec

import pymorphy2

# Загрузка словаря терминов
with open('terms_map.json', 'r', encoding='utf-8') as f:
    terms_map = json.load(f)

# Инициализация морфологического анализатора
morph = pymorphy2.MorphAnalyzer()

# Создание словаря форм
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

def replace_terms_in_text(text):
    replaced_text = text
    for old_form, new_form in forms_map.items():
        replaced_text = re.sub(r'\b' + re.escape(old_form) + r'\b', new_form, replaced_text)
    return replaced_text

# Папки
raw_dir = 'knowledge_base_raw'
output_dir = 'knowledge_base'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Обработка файлов
for filename in os.listdir(raw_dir):
    if filename.endswith('.txt'):
        filepath = os.path.join(raw_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Замена терминов
        new_content = replace_terms_in_text(content)

        # Сохранение в новую папку
        output_filepath = os.path.join(output_dir, filename)
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

print("Замена терминов завершена.")

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
