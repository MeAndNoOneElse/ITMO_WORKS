import cv2
import os

# Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.join(BASE_DIR, '..', 'task')
IMAGE_PATH = os.path.join(TASK_DIR, 'images', 'variant-9.png')
FLY_PATH = os.path.join(TASK_DIR, 'fly64.png')


def load_image(path, name="изображение"):
    """Загружает изображение по пути"""
    if not os.path.exists(path):
        print(f"Ошибка: не найдено {name} по пути {path}")
        return None
    img = cv2.imread(path)
    if img is None:
        print(f"Ошибка: не удалось прочитать {name}")
        return None
    print(f"Загружено: {name}")
    return img


def mode_marker_tracking():
    print("\nОТСЛЕЖИВАНИЕ МЕТКИ С КАМЕРЫ")

    image = load_image(IMAGE_PATH, "шаблон метки")
    if image is None:
        return

    # Загрузка мухи
    fly_img = None
    fly_alpha = None
    fly_loaded = False

    fly_data = cv2.imread(FLY_PATH, cv2.IMREAD_UNCHANGED)
    if fly_data is not None:
        if fly_data.shape[2] == 4:
            fly_img, fly_alpha = fly_data[:, :, :3], fly_data[:, :, 3]
        else:
            fly_img = fly_data
        fly_loaded = True
        print(f"Муха загружена: {fly_img.shape[1]}x{fly_img.shape[0]}px")
    else:
        print("Муха не найдена")

    # Подготовка шаблона
    template_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = template_gray.shape
    print(f"Размер метки: {w}x{h}px")

    # Масштабы для поиска
    scales = [0.1,0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75,0.8, 0.85, 0.95, 0.9 ]

    templates = [(cv2.resize(template_gray, (int(w*s), int(h*s))), s)
                 for s in scales if int(w*s) > 5 and int(h*s) > 5]

    # Камера
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Ошибка: камера не доступна!")
        return

    coordinates_list = []
    orb = cv2.ORB_create(nfeatures=1000)
    kp_template, des_template = orb.detectAndCompute(template_gray, None)

    smooth_factor = 0.7
    smoothed_center = None
    show_fly = False

    print("\nУПРАВЛЕНИЕ:")
    print("  ESC - выход в меню")
    print("  Ctrl+A - показать/скрыть муху")

    def overlay_fly(frame, fly_img, fly_alpha, pos):
        """Наложить муху на кадр"""
        x, y = pos
        h_fly, w_fly = fly_img.shape[:2]
        if x < 0 or y < 0 or x + w_fly > frame.shape[1] or y + h_fly > frame.shape[0]:
            return frame
        roi = frame[y:y + h_fly, x:x + w_fly]
        if fly_alpha is not None:
            alpha = fly_alpha / 255.0
            for c in range(3):
                roi[:, :, c] = (roi[:, :, c] * (1 - alpha) + fly_img[:, :, c] * alpha)
        else:
            frame[y:y + h_fly, x:x + w_fly] = fly_img
        return frame

    # Основной цикл
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_display = frame.copy()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Поиск на разных масштабах
        best_val = -1
        best_loc = best_w = best_h = None

        for tpl, scale in templates:
            h_tpl, w_tpl = tpl.shape
            if w_tpl > gray_frame.shape[1] or h_tpl > gray_frame.shape[0]:
                continue
            result = cv2.matchTemplate(gray_frame, tpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val > best_val:
                best_val, best_loc, best_w, best_h = max_val, max_loc, w_tpl, h_tpl

        # Проверка и обновление
        marker_found = False
        if best_val > 0.75 and best_loc is not None:
            top_left = best_loc
            bottom_right = (top_left[0] + best_w, top_left[1] + best_h)

            if 0 <= top_left[0] and 0 <= top_left[1] and bottom_right[0] <= frame.shape[1] and bottom_right[1] <= frame.shape[0]:
                roi = gray_frame[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                if roi.size > 0 and roi.shape[0] > 10 and roi.shape[1] > 10:
                    kp_roi, des_roi = orb.detectAndCompute(roi, None)
                    if des_template is not None and des_roi is not None:
                        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                        if len(bf.match(des_template, des_roi)) > 10:
                            best_val = min(best_val, 0.9)

            if best_val > 0.65:
                center_x = top_left[0] + best_w // 2
                center_y = top_left[1] + best_h // 2

                if smoothed_center is None:
                    smoothed_center = (center_x, center_y)
                else:
                    smoothed_center = (
                        int(smooth_factor * smoothed_center[0] + (1 - smooth_factor) * center_x),
                        int(smooth_factor * smoothed_center[1] + (1 - smooth_factor) * center_y)
                    )

                coordinates_list.append(smoothed_center)
                cv2.rectangle(frame_display, top_left, bottom_right, (0, 255, 0), 3)

                # Муха
                if show_fly and fly_loaded and fly_img is not None:
                    fly_h, fly_w = fly_img.shape[:2]
                    frame_display = overlay_fly(frame_display, fly_img, fly_alpha,
                                               (smoothed_center[0] - fly_w // 2, smoothed_center[1] - fly_h // 2))
                    cv2.circle(frame_display, smoothed_center, 3, (0, 0, 255), -1)
                    cv2.putText(frame_display, "FLY ON", (frame.shape[1] - 120, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                cv2.circle(frame_display, smoothed_center, 5, (0, 0, 255), -1)
                cv2.putText(frame_display, f"X={smoothed_center[0]} Y={smoothed_center[1]}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame_display, f"Trust: {best_val:.2f}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame_display, f"Count: {len(coordinates_list)}", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                marker_found = True

        if not marker_found:
            cv2.putText(frame_display, "Marker not found", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.putText(frame_display, "ESC-menu | Ctrl+A-fly", (10, frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow('Marker Tracking', frame_display)

        # Клавиши
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == 1:  # Ctrl+A
            show_fly = not show_fly
            print(f"Fly: {'ON' if show_fly else 'OFF'}")
        

    cap.release()
    cv2.destroyAllWindows()

    # Результаты
    print("\nSESSION RESULTS")
    if len(coordinates_list) > 0:
        avg_x = sum(c[0] for c in coordinates_list) / len(coordinates_list)
        avg_y = sum(c[1] for c in coordinates_list) / len(coordinates_list)
        all_x = [c[0] for c in coordinates_list]
        all_y = [c[1] for c in coordinates_list]

        print(f"Positions found: {len(coordinates_list)}")
        print(f"AVERAGE: X={avg_x:.1f} Y={avg_y:.1f}")
        print(f"X range: {min(all_x)}-{max(all_x)}")
        print(f"Y range: {min(all_y)}-{max(all_y)}")
    else:
        print("Marker not detected!")


if __name__ == "__main__":
    mode_marker_tracking()

