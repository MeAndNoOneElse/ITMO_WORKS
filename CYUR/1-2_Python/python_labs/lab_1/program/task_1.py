# ЗАДАНИЕ 1
# Сгенерировать при помощи escape-символов в консоли
# изображение флага, соответственно варианту
# (столбец "Страна").
# Вариант 9 (Финляндия)
def print_finland_flag():
    BLUE = '\033[94m██\033[0m'
    WHITE = '\033[97m██\033[0m'

    # Размеры флага (соотношение 18:11)
    width = 18
    height = 11

    print("Флаг Финляндии:")
    print()
    for y in range(1, height+1):
        line = ""
        for x in range(1, width+1):
            if (x >= 6 and x<=9) or (y >= 5 and y<=7):
                line += BLUE
            else:
                line += WHITE  # Белый фон
        print(line)
# if __name__ == "__main__":
print_finland_flag()
