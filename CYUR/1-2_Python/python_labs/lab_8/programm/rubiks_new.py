import cv2
import numpy as np


def mode_rubiks_cube():
    """Режим 3: Отслеживание кубика Рубика - улучшенная версия"""
    print("\n=== MODE 3: RUBIK'S CUBE TRACKING (ENHANCED) ===")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: camera not available!")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # HSV диапазоны для цветов
    color_ranges = {
        "Red": [(np.array([0, 120, 100]), np.array([10, 255, 255])),
                (np.array([160, 120, 100]), np.array([180, 255, 255]))],
        "Orange": [(np.array([5, 120, 100]), np.array([20, 255, 255]))],
        "Yellow": [(np.array([20, 100, 100]), np.array([35, 255, 255]))],
        "Green": [(np.array([35, 80, 80]), np.array([85, 255, 255]))],
        "Blue": [(np.array([85, 100, 100]), np.array([135, 255, 255]))],
        "White": [(np.array([0, 0, 200]), np.array([180, 30, 255]))]
    }

    color_bgr = {
        "Red": (0, 0, 255), "Orange": (0, 165, 255), "Yellow": (0, 255, 255),
        "Green": (0, 255, 0), "Blue": (255, 0, 0), "White": (255, 255, 255)
    }

    def find_color_squares(frame):
        """Находит все цветные квадраты на кубике"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv = cv2.GaussianBlur(hsv, (5, 5), 0)

        all_squares = []

        for color_name, ranges in color_ranges.items():
            # Создаем маску для текущего цвета
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            for lower, upper in ranges:
                mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lower, upper))

            # Морфологические операции для улучшения маски
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

            # Находим контуры
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                area = cv2.contourArea(cnt)
                # Ищем квадраты среднего размера (цветные стикеры кубика)
                if 200 < area < 5000:  # Настроенные пороги для стикеров
                    peri = cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)

                    # Проверяем, что это примерно квадрат
                    if len(approx) == 4:
                        x, y, w, h = cv2.boundingRect(cnt)
                        aspect_ratio = w / h
                        if 0.7 < aspect_ratio < 1.3:  # Примерно квадратный
                            # Вычисляем центр
                            center = (x + w // 2, y + h // 2)
                            all_squares.append({
                                'color': color_name,
                                'rect': (x, y, w, h),
                                'center': center,
                                'area': area
                            })

        return all_squares

    def find_face_grid(squares):
        """Находит сетку 3x3 из цветных квадратов"""
        if len(squares) < 5:  # Нужно минимум 5 квадратов для определения грани
            return None

        # Группируем близкие квадраты
        grouped = []
        used = set()

        for i, sq1 in enumerate(squares):
            if i in used:
                continue

            group = [sq1]
            used.add(i)

            for j, sq2 in enumerate(squares):
                if j in used:
                    continue

                # Проверяем расстояние между центрами
                dist = np.sqrt((sq1['center'][0] - sq2['center'][0]) ** 2 +
                               (sq1['center'][1] - sq2['center'][1]) ** 2)

                if dist < 100:  # Квадраты на одной грани
                    group.append(sq2)
                    used.add(j)

            if len(group) >= 4:  # Нашли потенциальную грань
                grouped.append(group)

        if not grouped:
            return None

        # Берем самую большую группу
        best_group = max(grouped, key=len)

        if len(best_group) < 4:
            return None

        # Находим границы грани
        all_x = [sq['center'][0] for sq in best_group]
        all_y = [sq['center'][1] for sq in best_group]

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        # Добавляем отступ
        margin = 30
        face_rect = (min_x - margin, min_y - margin,
                     max_x - min_x + 2 * margin, max_y - min_y + 2 * margin)

        return {
            'rect': face_rect,
            'squares': best_group,
            'count': len(best_group)
        }

    def draw_grid(frame, face_info):
        """Рисует сетку 3x3 и отображает цвета"""
        if not face_info:
            return

        x, y, w, h = face_info['rect']

        # Рисуем прямоугольник грани
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        # Рисуем сетку 3x3
        step_x = w // 3
        step_y = h // 3

        for i in range(1, 3):
            cv2.line(frame, (x + i * step_x, y), (x + i * step_x, y + h), (0, 255, 0), 2)
            cv2.line(frame, (x, y + i * step_y), (x + w, y + i * step_y), (0, 255, 0), 2)

        # Отображаем найденные квадраты
        for sq in face_info['squares']:
            rx, ry, rw, rh = sq['rect']
            cv2.rectangle(frame, (rx, ry), (rx + rw, ry + rh),
                          color_bgr[sq['color']], 2)
            cv2.circle(frame, sq['center'], 3, (0, 255, 0), -1)

        # Добавляем информацию
        info_text = f"Face found: {face_info['count']}/9 squares"
        cv2.putText(frame, info_text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Параметры для сглаживания
    smoothed_face = None
    smoothing_factor = 0.3

    print("CONTROLS: ESC - back to menu")
    print("Tip: Hold the Rubik's cube showing one face clearly\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 480))

        # Находим все цветные квадраты
        squares = find_color_squares(frame)

        # Находим грань кубика
        face_info = find_face_grid(squares)

        # Сглаживание для стабильности
        if face_info and smoothed_face:
            old_x, old_y, old_w, old_h = smoothed_face['rect']
            new_x, new_y, new_w, new_h = face_info['rect']

            smoothed_face['rect'] = (
                int(smoothing_factor * new_x + (1 - smoothing_factor) * old_x),
                int(smoothing_factor * new_y + (1 - smoothing_factor) * old_y),
                int(smoothing_factor * new_w + (1 - smoothing_factor) * old_w),
                int(smoothing_factor * new_h + (1 - smoothing_factor) * old_h)
            )
            smoothed_face['squares'] = face_info['squares']
            smoothed_face['count'] = face_info['count']
        elif face_info:
            smoothed_face = face_info

        # Рисуем результат
        if smoothed_face:
            draw_grid(frame, smoothed_face)
        else:
            cv2.putText(frame, "Rubik's cube face not found", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "Show a clear face with 9 colored squares", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Отображаем найденные квадраты (для отладки)
        debug_y = frame.shape[0] - 80
        cv2.putText(frame, f"Squares detected: {len(squares)}", (10, debug_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.putText(frame, "ESC - menu", (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("Rubik's Cube Tracker - Enhanced", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\nMode finished.")


if __name__ == "__main__":
    mode_rubiks_cube()