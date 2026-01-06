import requests
from bs4 import BeautifulSoup
import re
import unicodedata

def download_and_clean_page(url, min_paragraph_length=10):
    """
    Скачивает страницу Harry Potter Fandom (ru), тщательно очищает от мусора,
    включая ссылки, сноски, редакторские пометки, навигацию и т.д.
    Оставляет только основной повествовательный текст.
    
    :param url: URL страницы
    :param min_paragraph_length: минимальная длина абзаца в символах (фильтр от коротких мусорных строк)
    :return: Очищенный текст
    """
    # 1. Скачиваем страницу
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; KnowledgeBaseBot/1.0)"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Ошибка скачивания: {response.status_code} — {url}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 2. Находим основной контейнер контента
    content_div = soup.find('div', id='mw-content-text')
    if not content_div:
        raise ValueError("Не найден основной контент (mw-content-text)")
    
    # 3. Удаляем явно ненужные элементы
    unwanted_selectors = [
        'table.infobox',           # инфобокс справа
        'div.toc',                 # оглавление
        'div.navbox',              # навигационные боксы внизу
        'div.mw-references-wrap',  # список сносок
        'sup.reference',           # сами сноски [1][2]
        'div.hatnote',             # "Не путать с..."
        'div.aside',               # боковые вставки
        'figure',                  # изображения с подписями
        'gallery',                 # галереи
        'div.thumb',               # миниатюры изображений
        'span.mw-editsection',     # ссылки [править]
        'div.noprint',             # всё, что помечено как не для печати
        'aside'                    # новые портативные инфобоксы
    ]
    
    for selector in unwanted_selectors:
        for element in content_div.select(selector):
            element.decompose()
    
    # 4. Извлекаем текст из параграфов
    paragraphs = content_div.find_all('p')
    cleaned_paragraphs = []

    for p in paragraphs:
        text = p.get_text().strip()

        # Удаляем редакторские пометки типа [править | править код]
        text = re.sub(r'\[править\s*(?:\|[^\]]*)\]', '', text)

        # Удаляем остатки сносок в квадратных скобках в конце строки (например, [1][2])
        text = re.sub(r'\[\d+\]$', '', text).strip()

        # Удаляем строки вида "↑ 1 2 3 ..." или "Примечания"
        if text.startswith('↑') or '↑' in text:
            continue
        if re.match(r'^(Примечания|Ссылки|Литература|Источники|Внешние ссылки|См. также)$', text.strip()):
            continue

        # Нормализация юникода
        text = unicodedata.normalize('NFKC', text)

        # Удаляем множественные пробелы
        text = re.sub(r'\s+', ' ', text).strip()

        # Фильтруем слишком короткие параграфы (обычно это остатки мусора)
        if len(text) < min_paragraph_length and not text.endswith(('.', '!', '?', '»')):
            continue

        if text:  # добавляем только непустые
            cleaned_paragraphs.append(text)

    # 5. Объединяем в итоговый текст
    clean_text = '\n\n'.join(cleaned_paragraphs)
    
    return clean_text

# %%
# Пример использования в Jupyter
if __name__ == "__main__":
    test_urls = [
        "https://harrypotter.fandom.com/ru/wiki/Гарри_Поттер",
        "https://harrypotter.fandom.com/ru/wiki/Хогвартс",
        "https://harrypotter.fandom.com/ru/wiki/Волдеморт",
        "https://harrypotter.fandom.com/ru/wiki/Альбус_Дамблдор",
        "https://harrypotter.fandom.com/ru/wiki/Рон_Уизли",
        "https://harrypotter.fandom.com/ru/wiki/Гермиона_Грейнджер",
        "https://harrypotter.fandom.com/ru/wiki/Северус_Снегг",
        "https://harrypotter.fandom.com/ru/wiki/Драко_Малфой",
        "https://harrypotter.fandom.com/ru/wiki/Сириус_Блэк",
        "https://harrypotter.fandom.com/ru/wiki/Римус_Люпин",
        "https://harrypotter.fandom.com/ru/wiki/Минерва_МакГонагалл",
        "https://harrypotter.fandom.com/ru/wiki/Рубеус_Хагрид",
        "https://harrypotter.fandom.com/ru/wiki/Невилл_Долгопупс",
        "https://harrypotter.fandom.com/ru/wiki/Джинни_Уизли",
        "https://harrypotter.fandom.com/ru/wiki/Фред_Уизли",
        "https://harrypotter.fandom.com/ru/wiki/Джордж_Уизли",
        "https://harrypotter.fandom.com/ru/wiki/Гриффиндор",
        "https://harrypotter.fandom.com/ru/wiki/Слизерин",
        "https://harrypotter.fandom.com/ru/wiki/Когтевран",
        "https://harrypotter.fandom.com/ru/wiki/Пуффендуй",
        "https://harrypotter.fandom.com/ru/wiki/Квиддич",
        "https://harrypotter.fandom.com/ru/wiki/Философский_камень",
        "https://harrypotter.fandom.com/ru/wiki/Патронус",
        "https://harrypotter.fandom.com/ru/wiki/Крестраж",
        "https://harrypotter.fandom.com/ru/wiki/Министерство_магии",
        "https://harrypotter.fandom.com/ru/wiki/Азкабан",
        "https://harrypotter.fandom.com/ru/wiki/Косой_переулок",
        "https://harrypotter.fandom.com/ru/wiki/Турнир_Трёх_Волшебников",
        "https://harrypotter.fandom.com/ru/wiki/Битва_за_Хогвартс",
        "https://harrypotter.fandom.com/ru/wiki/Орден_Феникса"
    ]
    
    for url in test_urls:
        print(f"\n=== Обрабатываем: {url} ===")
        try:
            text = download_and_clean_page(url, min_paragraph_length=10)
            print(text[:800] + "\n...\n")
            # Сохраняем в файл (имя файла — из последней части URL)
            filename = url.split('/')[-1] + ".txt"
            with open(f"task2/knowledge_base_raw/{filename}", "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Сохранено в knowledge_base_raw/{filename}\n")
        except Exception as e:
            print(f"Ошибка: {e}")
