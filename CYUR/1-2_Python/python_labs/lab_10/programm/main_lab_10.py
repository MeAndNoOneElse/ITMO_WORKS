import json
import os
import pyaudio
import pyttsx3
import requests
from vosk import Model, KaldiRecognizer


# Словари перевода
WEATHER_RU = {
    "Sunny": "Солнечно",
    "Clear": "Ясно",
    "Partly cloudy": "Переменная облачность",
    "Cloudy": "Облачно",
    "Overcast": "Пасмурно",
    "Fog": "Туман",
    "Patchy rain possible": "Местами возможен дождь",
    "Patchy snow possible": "Местами возможен снег",
    "Blowing snow": "Метель",
    "Thundery outbreaks possible": "Возможна гроза",
    "Light rain": "Лёгкий дождь",
    "Moderate rain": "Умеренный дождь",
    "Heavy rain": "Сильный дождь",
    "Light rain shower": "Лёгкий ливень",
    "Light snow": "Лёгкий снег",
    "Moderate snow": "Умеренный снег",
    "Heavy snow": "Сильный снег",
    "Thunderstorm": "Гроза",
}
WIND_DIR_RU = {
    "N":   "северный",
    "NNE": "северо-северо-восточный",
    "NE":  "северо-восточный",
    "ENE": "востоко-северо-восточный",
    "E":   "восточный",
    "ESE": "востоко-юго-восточный",
    "SE":  "юго-восточный",
    "SSE": "юго-юго-восточный",
    "S":   "южный",
    "SSW": "юго-юго-западный",
    "SW":  "юго-западный",
    "WSW": "западо-юго-западный",
    "W":   "западный",
    "WNW": "западо-северо-западный",
    "NW":  "северо-западный",
    "NNW": "северо-северо-западный",
}

def translate_weather(desc: str) -> str:
    return WEATHER_RU.get(desc, desc)
def translate_wind_dir(code: str) -> str:
    return WIND_DIR_RU.get(code, code)


# Синтез речи

def speak(text: str) -> None:
    print(f"Ассистент: {text}")
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 250)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"Ошибка озвучивания: {e}")


# Распознавание речи (VOSK)

def init_vosk(model_path: str = "vosk-model-small-ru-0.22"):
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Модель VOSK не найдена: '{model_path}'\n"
        )
    model = Model(model_path)
    rec = KaldiRecognizer(model, 16000)
    return rec


def listen(rec: KaldiRecognizer) -> str:
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8000,
    )
    print("Слушаю...")

    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:
                    print(f"Вы сказали: {text}")
                return text
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


# Погода

WEATHER_URL = "https://wttr.in/Saint-Petersburg?format=j1"


def fetch_weather() -> dict | None:
    try:
        resp = requests.get(WEATHER_URL, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        speak(f"Ошибка при получении погоды: {e}")
        return None


def get_current(data: dict) -> dict:
    c = data["current_condition"][0]
    return {
        "temp":      int(c["temp_C"]),
        "feels":     int(c["FeelsLikeC"]),
        "desc":      translate_weather(c["weatherDesc"][0]["value"]),
        "wind_kmh":  int(c["windspeedKmph"]),
        "wind_dir":  translate_wind_dir(c["winddir16Point"]),
        "humidity":  int(c["humidity"]),
        "pressure":  int(c.get("pressure", 0)),
        "visibility": int(c.get("visibility", 0)),
    }


def get_tomorrow(data: dict) -> dict:
    day = data["weather"][1]  # индекс 0 — сегодня, 1 — завтра
    hourly = day["hourly"]
    avg_temp = sum(int(h["tempC"]) for h in hourly) // len(hourly)
    desc = translate_weather(day["hourly"][4]["weatherDesc"][0]["value"])
    max_temp = int(day["maxtempC"])
    min_temp = int(day["mintempC"])
    return {
        "desc":     desc,
        "avg_temp": avg_temp,
        "max_temp": max_temp,
        "min_temp": min_temp,
    }


# Обработчики команд

def cmd_weather():
    data = fetch_weather()
    if not data:
        return
    w = get_current(data)
    speak(
        f"Погода в Санкт-Петербурге: {w['desc']}. "
        f"Температура {w['temp']} градусов, ощущается как {w['feels']}. "
        f"Влажность {w['humidity']} процентов."
    )


def cmd_temperature():
    data = fetch_weather()
    if not data:
        return
    w = get_current(data)
    speak(f"Температура {w['temp']} градусов, ощущается как {w['feels']}.")


def cmd_wind():
    data = fetch_weather()
    if not data:
        return
    w = get_current(data)
    speak(f"Ветер {w['wind_dir']}, скорость {w['wind_kmh']} километров в час.")


def cmd_humidity():
    data = fetch_weather()
    if not data:
        return
    w = get_current(data)
    speak(f"Влажность воздуха: {w['humidity']} процентов.")


def cmd_pressure():
    data = fetch_weather()
    if not data:
        return
    w = get_current(data)
    mmhg = round(w["pressure"] * 0.750064)
    speak(f"Атмосферное давление: {mmhg} миллиметров ртутного столба.")


def cmd_forecast():
    data = fetch_weather()
    if not data:
        return
    t = get_tomorrow(data)
    speak(
        f"Прогноз на завтра: {t['desc']}. "
        f"Температура от {t['min_temp']} до {t['max_temp']} градусов."
    )


def cmd_walk():
    data = fetch_weather()
    if not data:
        return
    w = get_current(data)
    MIN_TEMP, MAX_WIND = 5, 15
    if w["temp"] < MIN_TEMP:
        speak(f"Не рекомендуется: слишком холодно — {w['temp']} градусов.")
    elif w["wind_kmh"] > MAX_WIND:
        speak(f"Не рекомендуется: сильный ветер — {w['wind_kmh']} км/ч.")
    else:
        speak(f"Хорошая погода для прогулки! {w['temp']} градусов, ветер {w['wind_kmh']} км/ч.")


def cmd_record():
    data = fetch_weather()
    if not data:
        return
    w = get_current(data)
    try:
        with open("weather_log.txt", "a", encoding="utf-8") as f:
            f.write(
                f"{w['desc']}, {w['temp']}°C (ощущается {w['feels']}°C), "
                f"ветер {w['wind_dir']} {w['wind_kmh']} км/ч, "
                f"влажность {w['humidity']}%, давление {round(w['pressure'] * 0.750064)} мм рт.ст.\n"
            )
        speak("Данные записаны в файл weather_log.txt.")
    except Exception as e:
        speak(f"Ошибка записи: {e}")


def cmd_help():
    speak(
        "Доступные команды: "
        "погода, температура, ветер, влажность, давление, прогноз, "
        "прогулка, записать, помощь, выход."
    )


# Маршрутизация команд

ROUTES = [
    (("температура",),                cmd_temperature),
    (("погода",),                     cmd_weather),
    (("ветер", "направление"),        cmd_wind),
    (("влажность",),                  cmd_humidity),
    (("давление",),                   cmd_pressure),
    (("прогноз", "завтра"),           cmd_forecast),
    (("прогулка",),                   cmd_walk),
    (("записать", "запись"),          cmd_record),
    (("помощь", "команды", "помоги"), cmd_help),
]


def process(command: str) -> bool:
    """Выполнить команду. Вернуть False если нужно выйти."""
    if any(w in command for w in ("выход", "пока", "до свидания")):
        speak("До свидания!")
        return False

    for keywords, handler in ROUTES:
        if any(k in command for k in keywords):
            handler()
            return True

    speak("Команда не распознана.")
    return True


# Точка входа

def main():
    rec = init_vosk()
    speak("Привет! Скажите команду или «помощь».")

    while True:
        command = listen(rec)
        if command and not process(command):
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nАссистент уехал в отпуск.")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Критическая ошибка: {e}")
