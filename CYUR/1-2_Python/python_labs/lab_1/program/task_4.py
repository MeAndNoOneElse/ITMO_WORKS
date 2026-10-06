#ЗАДАНИЕ 4
#Используя прилагаемый файл с числовой последовательностью sequence.txt,
# вывести диаграмму процентного соотношения согласно варианту.
# Числа от 5 до 10 и числа от -5 до -10, остальные отбросить
def read_sequence(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        numbers = [float(line.strip()) for line in file if line.strip()]
    return numbers


def filter_numbers(numbers):
    filtered = []
    discarded = []
    for num in numbers:
        if (5 <= num <= 10) or (-10 <= num <= -5):
            filtered.append(num)
        else:
            discarded.append(num)

    return filtered, discarded

def calculate_percentages(numbers):
    if not numbers:
        return {}

    # Группируем числа по диапазонам
    ranges = {
        " 5.0 - 6.0": 0,
        " 6.0 - 7.0": 0,
        " 7.0 - 8.0": 0,
        " 8.0 - 9.0": 0,
        " 9.0 - 10.0": 0,
        "-5.0 - -6.0": 0,
        "-6.0 - -7.0": 0,
        "-7.0 - -8.0": 0,
        "-8.0 - -9.0": 0,
        "-9.0 - -10.0": 0
    }

    for num in numbers:
        if 5 <= num < 6:
            ranges[" 5.0 - 6.0"] += 1
        elif 6 <= num < 7:
            ranges[" 6.0 - 7.0"] += 1
        elif 7 <= num < 8:
            ranges[" 7.0 - 8.0"] += 1
        elif 8 <= num < 9:
            ranges[" 8.0 - 9.0"] += 1
        elif 9 <= num <= 10:
            ranges[" 9.0 - 10.0"] += 1
        elif -6 <= num < -5:
            ranges["-5.0 - -6.0"] += 1
        elif -7 <= num < -6:
            ranges["-6.0 - -7.0"] += 1
        elif -8 <= num < -7:
            ranges["-7.0 - -8.0"] += 1
        elif -9 <= num < -8:
            ranges["-8.0 - -9.0"] += 1
        elif -10 <= num < -9:
            ranges["-9.0 - -10.0"] += 1

    # Преобразуем в проценты
    total = len(numbers)
    percent = {}
    for range_name, count in ranges.items():
        if (count > 0):
            percent[range_name] = (count / total) * 100

    return percent

def print_statistics(filtered, discarded, percentages):

    total_numbers = len(filtered) + len(discarded)
    print(f"Всего чисел в файле: {total_numbers}")
    print(f"Отфильтровано чисел: {len(filtered)}")
    print(f"Отброшено чисел: {len(discarded)}")

    if total_numbers > 0:
        print(f"Процент отфильтрованных: {(len(filtered) / total_numbers * 100):.1f}%")
    print("+"+"─"*44+"+")
    # Восстанавливаем количество чисел из процентов
    for range_name, percentage in sorted(percentages.items(), key=lambda x: sort_key(x[0])):
        count = int((percentage / 100) * len(filtered))
        bar_length = int((percentage / 100)*50)
        bar = "█" * bar_length

        print(f"|{range_name:12}| {bar:10} | {count:2} чисел ({percentage:4.1f}%)|")
    print("+" + "─" * 44 + "+")

def sort_key(range_name):
    """Функция для сортировки диапазонов"""
    if range_name.startswith('-'):
        return float(range_name.split()[0])
    else:
        return float(range_name.split('-')[0])


def main():
    try:
        # Чтение данных
        numbers = read_sequence("sequence.txt")
        # Фильтрация
        filtered, discarded = filter_numbers(numbers)


        if not filtered:
            print("Нет чисел, соответствующих условиям фильтрации")
            return

        # Расчет процентов
        percentages = calculate_percentages(filtered)
        # Статистика
        print_statistics(filtered, discarded, percentages)
    except FileNotFoundError:
        print("Файл sequence.txt не найден")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
main()