def parse_csv_file(filename):
    def remove_quotes(value):
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            return value[1:-1]
        return value

    def parse_line(line):
        result = []
        current_field = ""
        in_quotes = False

        i = 0
        while i < len(line):
            char = line[i]

            if char == '"':
                if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                    current_field += '"'
                    i += 1
                else:
                    in_quotes = not in_quotes
            elif char == ';' and not in_quotes:
                # Конец поля
                result.append(remove_quotes(current_field.strip()))
                current_field = ""
            else:
                current_field += char

            i += 1

        # Добавляем последнее поле
        result.append(remove_quotes(current_field.strip()))

        return result

    data = []

    try:
        with open(filename, 'r', encoding='windows-1251') as file:
            # Читаем заголовок
            header_line = file.readline().strip()
            if header_line:
                headers = parse_line(header_line)
                data.append(headers)

            # Читаем остальные строки
            for line in file:
                line = line.strip()
                if line:  # Пропускаем пустые строки
                    row = parse_line(line)
                    data.append(row)

    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return []

    return data



def publisher_list(data):
    publishers = set()
    for row in data:
        publishers.add(row[4])
    print("Издательства без повторений")
    print(*sorted(publishers), sep="\n")

def popylar_books(data):
    books = []
    top20 = sorted(data[1:], key=lambda row: int(row[5]), reverse= True)[:20]
    for row in top20:
        l = f"  {row[5]:5}- {row[1]}"
        books.append(l)
    print("Топ 20 книг по кол-ву скачиваний")
    print("Кол-во | Название")
    print(*books, sep="\n")

date = parse_csv_file("books-en.csv")
# publisher_list(date)
popylar_books(date)

