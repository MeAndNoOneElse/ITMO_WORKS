# ДОП.ЗАДАНИЕ
# блок падает, пока не касается земли, можно задать расстояние, с которого падает
# и уровень земли
import os
import time


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def falling_block_animation(height, ground_level):
    BLOCK = "██"
    EMPTY = "  "
    EARTH = "||" * 9

    def create_frame(height, block_pos, ground_level):
        frame = []
        for i in range(height):
            if i == block_pos:
                frame.append(EMPTY * 4 + BLOCK)
            elif i == ground_level:
                frame.append(EARTH)
            else:
                frame.append("")
        return frame

    frames = []

    # Создаем кадры падения
    for pos in range(height):
        if pos < ground_level:  # Блок может быть на уровне земли
            frames.append(create_frame(height, pos, ground_level))

    # Анимация
    for i in range(len(frames)):
        clear_console()
        print("Падающий блок:")
        frame = frames[i]
        for line in frame:
            print(line)
        time.sleep(0.1)


height = 10
ground_level = 5
falling_block_animation(height, ground_level)
