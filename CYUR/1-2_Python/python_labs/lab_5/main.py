import re
import csv
from typing import List, Tuple


def task1(text: str) -> Tuple[List[str], List[str]]:
    #  заканчивающаяся на "e"
    words_ending_e = re.findall(r'\b[a-zA-Zа-яА-ЯёЁ]+е\b', text)
    #  в круглых скобках (целые и дробные)
    numbers_in_parentheses = re.findall(r'\((\d+(?:[.,]\d+)?)\)', text)
    return words_ending_e, numbers_in_parentheses

def task2(html_text: str) -> List[str]:
    sizes = []
    #  все теги img
    img_tags = re.findall(r'<img[^>]*>', html_text, re.IGNORECASE)
    for img_tag in img_tags:
        #  width
        width_match = re.search(r'width\s*=\s*[""]?(\d+)', img_tag, re.IGNORECASE)
        #  height
        height_match = re.search(r'height\s*=\s*[""]?(\d+)', img_tag, re.IGNORECASE)
        if width_match and height_match:
            size = f"{width_match.group(1)}x{height_match.group(1)}"
            sizes.append(size)
        elif width_match:
            sizes.append(f"width: {width_match.group(1)}")
        elif height_match:
            sizes.append(f"height: {height_match.group(1)}")

    # Убираем дубликаты
    seen = set()
    unique_sizes = []
    for size in sizes:
        if size not in seen:
            seen.add(size)
            unique_sizes.append(size)

    return unique_sizes


def task3(text: str) -> List[Tuple[str, str, str, str, str]]:
    patterns = {
        'id': r'\b(\d{1,3})\b',
        'email': r'([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        'date': r'(\d{4}-\d{2}-\d{2})',
        'website': r'(https?://[^\s]+)',
        'surname': r'\b([A-Z][a-z]+)\b'
    }
    combined_pattern = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in patterns.items())

    all_matches = []
    for match in re.finditer(combined_pattern, text):
        for name, value in match.groupdict().items():
            if value is not None:
                all_matches.append((name, value))
                break

    records = []
    i = 0
    while i < len(all_matches):
        record = {'id': '', 'surname': '', 'email': '', 'date': '', 'website': ''}
        filled = 0
        seen = set()
        while i < len(all_matches) and filled < 5:
            dtype, value = all_matches[i]
            # Не дублируем одинаковый тип в одной записи
            if dtype not in seen:
                record[dtype] = value
                filled += 1
                seen.add(dtype)
            i += 1
        if record['id']:
            records.append((
                record['id'],
                record['surname'],
                record['email'],
                record['date'],
                record['website']
            ))
    return records

def save_database_to_csv(records: List[Tuple[str, str, str, str, str]], filename: str):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Surname', 'Email', 'Registration_Date', 'Website'])
        writer.writerows(records)


def task_dop(text: str) -> Tuple[List[str], List[str], List[str]]:
    # Email - с пробелом перед ним
    email_pattern = r'\s([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    # URL - с пробелом перед ним
    url_pattern = r'\s(https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    # Даты - различные форматы
    date_patterns = [
        r'\s(\d{4}[-/\.]\d{2}[-/\.]\d{2})',  # YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD
        r'\s(\d{2}[-/\.]\d{2}[-/\.]\d{4})',  # DD-MM-YYYY, DD/MM/YYYY, DD.MM.YYYY
    ]
    # Поиск
    emails = re.findall(email_pattern, text)
    urls = re.findall(url_pattern, text)
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text))
    return dates, emails, urls

def main():
    # Загрузка файлов
    with open('task1-ru.txt', 'r', encoding='utf-8') as f:
        task1_text = f.read()

    with open('task2.html', 'r', encoding='utf-8') as f:
        task2_text = f.read()

    with open('task3.txt', 'r', encoding='utf-8') as f:
        task3_text = f.read()

    with open('task_add.txt', 'r', encoding='utf-8') as f:
        task_add_text = f.read()

    # Задание 1
    print("\nЗАДАНИЕ 1")
    words_e, numbers_parens = task1(task1_text)
    print(f"\nСлова, заканчивающиеся на 'e': {len(words_e)} шт.")
    print(*words_e)
    print(f"Числа в круглых скобках: {len(numbers_parens)} шт.")
    print(*numbers_parens)
    input("\nНажмите Enter для перехода к следующему заданию ...")

    # Задание 2
    print("\nЗАДАНИЕ 2")
    image_sizes = task2(task2_text)
    print("\nУникальные размеры изображений: " , *image_sizes)
    input("\nНажмите Enter для перехода к следующему заданию ...")


    # Задание 3
    print("\nЗАДАНИЕ 3")
    database = task3(task3_text)
    save_database_to_csv(database, 'task3_result.csv')
    print(f"\nВсего записей: {len(database)}")
    print("Данные сохранены в файл: task3_result.csv")
    input("\nНажмите Enter для перехода к следующему заданию ...")


    # Доп
    print("\nДОП")
    dates, emails, urls = task_dop(task_add_text)
    print(f"\nНайдено: {len(dates)} дат, {len(emails)} email, {len(urls)} URL")
    print(*dates)
    print(*emails)
    print(*urls)


if __name__ == "__main__":
    main()
