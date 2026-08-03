#ЗАДАНИЕ 2
#Сгенерировать в консоли повторяющийся узор (i)
def print_double_circle(n):
    BLACK = '█'
    WHITE = ' '
    print("Два кружочка:")
    print()
    # print(" 0         10        20        30        40        50")
    # print(" 012345678901234567890123456789012345678901234567890")
    for y in range(n//4+1):
        line = ""
        for x in range(n+1):
            if ((x/2-n/8)**2+(y-n/8)**2 <= (n/8)**2 or
                ((x/2-n/8*3)**2+(y-n/8)**2 <= (n/8)**2)):
                line += BLACK
            else:
                line += WHITE  # Белый фон

        print(line)
print_double_circle(48)
