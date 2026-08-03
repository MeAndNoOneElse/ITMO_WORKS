import cv2
import os

# Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.join(BASE_DIR, '..', 'task')
IMAGE_PATH = os.path.join(TASK_DIR, 'images', 'variant-9.png')


def load_image(path, name="изображение"):
    """Загружает изображение по пути"""
    if not os.path.exists(path):
        print(f"Ошибка: не найдено {name} по пути {path}")
        return None
    img = cv2.imread(path)
    if img is None:
        print(f"Ошибка: не удалось прочитать {name}")
        return None
    print(f"✓ Загружено: {name}")
    return img


def mode_pyramid():
    """Режим 1: Вывести пирамиду изображений"""
    print("\n=== РЕЖИМ 1: ПИРАМИДА ИЗОБРАЖЕНИЙ ===")

    image = load_image(IMAGE_PATH, "тестовое изображение")
    if image is None:
        return

    h, w = image.shape[:2]
    h, w = int(h * 0.8), int(w * 0.8)
    first_scaled = cv2.resize(image, (w, h))

    # Создаём пирамиду с разными коэффициентами уменьшения
    pyramid = [first_scaled]
    scale_factors = [2, 3, 4, 5]  # Коэффициенты уменьшения для остальных

    for scale in scale_factors:
        new_h, new_w = h // scale, w // scale
        resized = cv2.resize(image, (new_w, new_h))
        pyramid.append(resized)


    # Создаём композицию пирамиды с расстояниями
    rows = []
    original_h = h
    
    for level in range(5):
        num_images = level + 1
        row_images = [pyramid[level] for _ in range(num_images)]

        # Объединяем изображения в строке горизонтально
        row = cv2.hconcat(row_images)
        rows.append(row)
    
    # Приводим все строки к одинаковой ширине
    max_width = max(r.shape[1] for r in rows)
    for i in range(len(rows)):
        current_width = rows[i].shape[1]
        if current_width < max_width:
            padding = max_width - current_width
            rows[i] = cv2.copyMakeBorder(rows[i], 0, 0, 0, padding, cv2.BORDER_CONSTANT, value=(0, 0, 0))

    # Объединяем строки вертикально
    result = cv2.vconcat(rows)

    print(f"✓ Пирамида размером {result.shape[1]}x{result.shape[0]} пиксель создана")
    print("Нажмите любую клавишу для выхода...\n")

    cv2.imshow('Пирамида изображений', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("✓ Пирамида показана\n")


if __name__ == "__main__":
    mode_pyramid()

