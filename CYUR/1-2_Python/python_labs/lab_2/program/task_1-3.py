import time


def parse_csv(filename):
    data = []
    with open(filename, 'r', encoding='windows-1251') as file:
        for line in file:
            # Убираем символы переноса строки и разделяем по ;
            row = line.strip().split(';')
            data.append(row)
    return data


def name(str):
    if "#" in str:
        dot_space_index = str.find(". ")
        return str[dot_space_index + 2:]
    return str


def year(str):
    return str[6:10]


def random(start, stop):
    return start + time.perf_counter_ns() % stop


def task_1(data):
    sum = 0
    for row in data:
        if len(row[1]) > 30:
            sum += 1
    print(sum)


def task_2(data, autor):
    ans = []
    for row in data:

        if (row[3].lower() == autor.lower()) and int(float(row[7])) >= 200:
            # print(row[3].lower(), row[7])
            ans.append(f"\tНазвание:{name(row[1]):20}\n\tЦена:{row[7]:4}руб.\n")
    if len(ans) == 0:
        print("Нет данных")
    else:
        print("Книги автора: " + autor)
        print(*ans)


def task_3(data):
    random_list = []
    number_list = []
    while len(random_list) < 20:
        m = random(1, len(data))  # Псевдослучайная функция, которая вернёт число от 1 до длинны data
        if m not in number_list:
            number_list.append(m)
            random_list.append(f'"{data[m][3]}"."{name(data[m][1])}"-{year(data[m][6])}год')
        else:
            continue
    with open('bibliographic_references.txt', 'w', encoding='utf-8') as f:
        n = 1
        for row in random_list:
            f.write(f"{n}. {row}\n")
            n += 1
    print("Сгенерировано 20 ссылок. они находятся в файле bibliographic_references.txt")


data = parse_csv('books.csv')
print("Результат task_1:", end=" ")
task_1(data)
print("Введите имя автора из колонки автор")
s = input()
print("Результат task_2:")
task_2(data, s)
print("Результат task_3:")
task_3(data)
