import requests
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO

# Часть 1: OpenWeatherMap API

OWM_API_KEY = "94210884db92ab52ce306f0466046ebc"
OWM_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city_name):
    params = {
        "q": city_name,
        "appid": OWM_API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    try:
        response = requests.get(OWM_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Персонаж '{city_name}' не найден")
        print(f"Ошибка: {e}")
        return False

    data = response.json()

    main = data.get("main", {})
    weather = data.get("weather", [{}])[0]
    wind = data.get("wind", {})

    print(f"  Погода: {data['name']}, {data['sys'].get('country', '')}")
    print(f"{'='*40}")
    print(f"  Температура:     {main.get('temp', 'N/A')}°C")
    print(f"  Ощущается как:   {main.get('feels_like', 'N/A')}°C")
    print(f"  Влажность:       {main.get('humidity', 'N/A')}%")
    print(f"  Давление:        {main.get('pressure', 'N/A')} hPa")
    print(f"  Описание:        {weather.get('description', 'N/A')}")
    print(f"  Ветер:           {wind.get('speed', 'N/A')} м/с")

    return True


# Часть 2: Rick and Morty API (Вариант 9)

BASE_URL = "https://rickandmortyapi.com/api/character"


def get_character(name):
    params = {"name": name}

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Персонаж '{name}' не найден")
        print(f"Ошибка: {e}")
        
        return

    data = response.json()


    char = data["results"][0]
    origin = char.get("origin", {})
    location = char.get("location", {})
    image_url = char.get("image", "")

    print(f"  Rick and Morty: {char['name']}")
    print(f"{'='*40}")
    print(f"  Пол:             {char['gender']}")
    print(f"  Вид:             {char['species']}")
    print(f"  Статус:          {char['status']}")
    print(f"  Родной мир:      {origin.get('name', 'неизвестно')}")
    print(f"  Текущее место:   {location.get('name', 'неизвестно')}")

    return image_url


def get_random_character():
    """Получить и вывести случайного персонажа."""
    import random

    try:
        info_resp = requests.get("https://rickandmortyapi.com/api/character", timeout=10)
        info_resp.raise_for_status()
        total = info_resp.json().get("info", {}).get("count", 1)
    except requests.RequestException as e:
        print(f"Ошибка сети: {e}")
        return

    char_id = random.randint(1, total)

    try:
        response = requests.get(f"https://rickandmortyapi.com/api/character/{char_id}", timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка сети: {e}")
        return

    char = response.json()
    origin = char.get("origin", {})
    location = char.get("location", {})

    print(f"  Rick and Morty: {char['name']}")
    print(f"{'='*40}")
    print(f"  Пол:             {char['gender']}")
    print(f"  Вид:             {char['species']}")
    print(f"  Статус:          {char['status']}")
    print(f"  Родной мир:      {origin.get('name', 'неизвестно')}")
    print(f"  Текущее место:   {location.get('name', 'неизвестно')}")


# Часть 3 : Генератор котиков (tkinter + cataas.com)

CATAAS_URL = "https://cataas.com/cat/gif"


class CatosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор котиков")
        self.root.geometry("500x550")

        self.label = tk.Label(root, text="Нажмите кнопку для загрузки котика")
        self.label.pack(pady=5)

        self.image_label = tk.Label(root)
        self.image_label.pack(pady=5)

        self.btn_next = tk.Button(root, text="Следующий котик", command=self.load_image)
        self.btn_next.pack(pady=5)

        # Для анимации GIF
        self._animation_id = None
        self._gif_frames = []
        self._gif_delays = []
        self._current_frame = 0

        self.load_image()

    def load_image(self):
        self._stop_animation()
        self.btn_next.config(state="disabled")
        self.label.config(text="Загрузка котика...")
        self.root.update()
        self.root.after(10)  # даём интерфейсу обновиться

        try:
            response = requests.get(CATAAS_URL, timeout=15)
            response.raise_for_status()

            gif_data = BytesIO(response.content)
            gif = Image.open(gif_data)
            mime = gif.format

            if mime == "GIF":
                self._load_animated_gif(gif)
                self._play_animation()
                self.label.config(text="Мяу!")
            else:
                # Fallback: обычная статичная картинка
                img = gif.resize((400, 400), Image.LANCZOS)
                self.photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.photo)
                self.label.config(text="Мяу!")
        except (requests.RequestException, Exception) as e:
            self.label.config(text=f"Ошибка: {e}")

        self.btn_next.config(state="normal")

    def _load_animated_gif(self, gif):
        self._gif_frames = []
        self._gif_delays = []
        self._current_frame = 0

        try:
            while True:
                frame = gif.convert("RGBA")
                w, h = frame.size
                ratio = min(400 / w, 400 / h)
                new_w, new_h = int(w * ratio), int(h * ratio)
                frame = frame.resize((new_w, new_h), Image.LANCZOS)
                self._gif_frames.append(ImageTk.PhotoImage(frame))

                delay = gif.info.get("duration", 100)  # мс
                self._gif_delays.append(delay)

                gif.seek(gif.tell() + 1)
        except EOFError:
            pass



    def _play_animation(self):
        """Анимировать GIF покадрово через after()."""
        if not self._gif_frames:
            return
        self.image_label.config(image=self._gif_frames[self._current_frame])
        delay = self._gif_delays[self._current_frame]
        self._current_frame = (self._current_frame + 1) % len(self._gif_frames)
        self._animation_id = self.root.after(delay, self._play_animation)

    def _stop_animation(self):
        """Остановить текущую анимацию."""
        if self._animation_id is not None:
            self.root.after_cancel(self._animation_id)
            self._animation_id = None
        self._gif_frames = []
        self._gif_delays = []
        self._current_frame = 0
        self.image_label.config(image="")


# Главная точка входа

def task_1_weather():
    """Задание 1: погода."""
    city = input("\nВведите город: ").strip()
    if city:
        get_weather(city)


def task_2_rick_morty():
    """Задание 2: персонаж."""
    name = input("\nВведите имя персонажа (Enter — случайный): ").strip()
    if name:
        get_character(name)
    else:
        get_random_character()


def task_3_cats():
    print("Открываю генератор котиков...")
    root = tk.Tk()
    app = CatosApp(root)
    root.mainloop()


if __name__ == "__main__":
    print("=== Лабораторная работа №7: Работа с API ===\n")

    tasks = {
        "1": ("Погода в городе", task_1_weather),
        "2": ("Персонаж Rick and Morty", task_2_rick_morty),
        "3": ("Генератор котиков", task_3_cats),
    }

    while True:
        print("\nВыберите задание:")
        for key, (label, _) in tasks.items():
            print(f"  {key} — {label}")
        print("  q — выход")

        choice = input("Ваш выбор: ").strip().lower()
        if choice == "q":
            print("Выход.")
            break
        if choice in tasks:
            label, func = tasks[choice]
            print(f"\n--- {label} ---")
            func()
            print("-" * 30)
        else:
            print("Некорректный выбор, попробуйте снова.")
