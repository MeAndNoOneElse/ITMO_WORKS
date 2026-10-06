#ЗАДАНИЕ 3
# Сгенерировать в консоли график функции (1 четверти) при помощи escape-символов,
# минимум 9 строк в высоту (y = x / 2).
def plot_function_with_grid():
    # Более детальный график с сеткой
    print("График функции y = x/2 с сеткой")

    print("y ↑")

    height = 10
    width = 20

    for y in range(height - 1, -1, -1):
        line = ""
        for x in range(width):
            real_y = x / 2

            if real_y == y:
                line += "● "  # Точка графика
            elif y == 0 and x > 0:
                if x==19: line += "──>"
                else:line += "──"  # Ось X
            elif x == 0 and y > 0:
                line += "│ "  # Ось Y
            else:
                line += "· "  # Пустое пространство
        print(f"{y:1} {line}")

    print(" " + "".join(f"{i:2}" for i in range(width))+ " x" )


plot_function_with_grid()
