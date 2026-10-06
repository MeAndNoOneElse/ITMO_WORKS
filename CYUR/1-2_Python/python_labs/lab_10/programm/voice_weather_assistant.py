import speech_recognition as sr
import pyttsx3
import requests
from typing import Optional, Dict, Any
import time


class WeatherAssistant:
    """Голосовой ассистент для получения информации о погоде в Санкт-Петербурге"""

    def __init__(self):
        """Инициализация ассистента"""
        # Инициализация синтеза речи
        self.tts_rate = 250
        self.engine = self._init_tts_engine()

        # Инициализация распознавания речи
        self.recognizer = sr.Recognizer()
        self.weather_url = "https://wttr.in/Saint-Petersburg?format=2"
        self.weather_url_detailed = "https://wttr.in/Saint-Petersburg?format=j1"

        # Пороги для рекомендаций прогулки
        self.min_temp = 5  # минимальная температура для прогулки (градусы)
        self.max_wind = 15  # максимальная скорость ветра для прогулки (км/ч)

        self.weather_data = None
        self.is_running = True

        # Порядок важен: сохраняем исходный приоритет распознавания команд
        self.command_routes = [
            (('погода',), self.handle_weather_command),
            (('ветер',), self.handle_wind_command),
            (('направление',), self.handle_direction_command),
            (('записать',), self.handle_record_command),
            (('прогулка',), self.handle_walk_command),
            (('выход', 'пока', 'до свидания'), self.handle_exit_command),
            (('помощь', 'команды', 'помоги'), self.show_help),
        ]

    def _init_tts_engine(self):
        """Создать и настроить движок озвучивания с fallback для Windows"""
        try:
            engine = pyttsx3.init('sapi5')
        except Exception:
            engine = pyttsx3.init()
        engine.setProperty('rate', self.tts_rate)
        return engine

    def _reset_tts_engine(self):
        """Переинициализировать движок озвучивания в случае ошибки"""
        if self.engine:
            self.engine.stop()
        self.engine = self._init_tts_engine()

    def speak(self, text: str) -> None:
        """Произнести текст"""
        print(f"Ассистент: {text}")

        try:
            # Создаём новый движок для каждой фразы
            engine = pyttsx3.init()
            engine.setProperty('rate', self.tts_rate)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"Ошибка озвучивания: {e}")

    def listen(self) -> Optional[str]:
        try:
            print("Слушаю...")
            try:
                with sr.Microphone() as source:
                    # Регулировка уровня шума
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
                
                text = self.recognizer.recognize_google(audio, language='ru-RU')
                print(f"Вы сказали: {text}")
                return text.lower()
            
            except sr.UnknownValueError:
                self.speak("Извините, я не смог распознать вашу команду")
                return None
            except sr.RequestError as e:
                self.speak(f"Ошибка сервиса распознавания: {str(e)}")
                return None

        except Exception as e:
            error_str = str(e)
            if "PyAudio" in error_str or "module" in error_str.lower():
                self.speak(f"Ошибка при прослушивании: {error_str}")
                return None


    def get_weather(self) -> bool:
        """Получить информацию о погоде"""
        try:
            response = requests.get(self.weather_url_detailed, timeout=5)
            response.raise_for_status()
            self.weather_data = response.json()
            return True
        except requests.RequestException as e:
            self.speak(f"Ошибка при получении данных о погоде: {str(e)}")
            return False

    def parse_weather_simple(self) -> Optional[str]:
        """Получить простую информацию о погоде"""
        try:
            response = requests.get(self.weather_url, timeout=5)
            response.raise_for_status()
            return response.text.strip()
        except requests.RequestException as e:
            self.speak(f"Ошибка при получении данных: {str(e)}")
            return None

    def extract_weather_info(self) -> Dict[str, Any]:
        """Извлечь информацию о погоде из JSON"""
        try:
            current = self.weather_data['current_condition'][0]
            info = {
                'temperature': int(current['temp_C']),
                'weather': current['weatherDesc'][0]['value'],
                'wind_speed': int(current['windspeedKmph']),
                'wind_dir': current['winddir16Point'],
                'humidity': int(current['humidity']),
                'feels_like': int(current['FeelsLikeC'])
            }
            return info
        except (KeyError, IndexError, TypeError, ValueError) as e:
            self.speak(f"Ошибка при обработке данных о погоде: {str(e)}")
            return {}

    def get_current_weather_info(self) -> Optional[Dict[str, Any]]:
        """Получить и вернуть погодные данные или None при ошибке"""
        if not self.get_weather():
            return None
        info = self.extract_weather_info()
        return info if info else None

    def handle_weather_command(self) -> None:
        """Обработка команды 'погода'"""
        info = self.get_current_weather_info()
        if not info:
            return

        response = f"Температура в Санкт-Петербурге: {info['temperature']} градусов. " \
                   f"Ощущается как {info['feels_like']} градусов. " \
                   f"Погода: {info['weather']}. " \
                   f"Влажность: {info['humidity']}%."
        self.speak(response)

    def handle_wind_command(self) -> None:
        info = self.get_current_weather_info()
        if not info:
            return

        response = f"Скорость ветра: {info['wind_speed']} километров в час. " \
                   f"Направление ветра: {info['wind_dir']}."
        self.speak(response)

    def handle_direction_command(self) -> None:
        info = self.get_current_weather_info()
        if not info:
            return

        response = f"Ветер дует с направления: {info['wind_dir']}."
        self.speak(response)

    def handle_record_command(self) -> None:
        info = self.get_current_weather_info()
        if not info:
            return

        try:
            with open('weather_log.txt', 'a', encoding='utf-8') as f:
                f.write(f"Температура: {info['temperature']}°C, "
                       f"Погода: {info['weather']}, "
                       f"Ветер: {info['wind_speed']} км/ч, "
                       f"Направление: {info['wind_dir']}\n")
            self.speak("Информация о погоде записана в файл weather_log.txt")
        except Exception as e:
            self.speak(f"Ошибка при записи в файл: {str(e)}")

    def handle_walk_command(self) -> None:
        info = self.get_current_weather_info()
        if not info:
            return

        temp = info['temperature']
        wind = info['wind_speed']

        if temp < self.min_temp:
            response = f"Не рекомендуется. Слишком холодно: {temp} градусов. " \
                      f"Минимальная температура для прогулки: +{self.min_temp} градусов."
        elif wind > self.max_wind:
            response = f"Не рекомендуется. Слишком сильный ветер: {wind} км/ч. " \
                      f"Максимальная скорость ветра: {self.max_wind} км/ч."
        else:
            response = f"Рекомендуется! Приятная температура: {temp} градусов и " \
                      f"ветер {wind} км/ч. Хорошая погода для прогулки!"

        self.speak(response)

    def handle_exit_command(self) -> None:
        self.speak("До свидания!")
        self.is_running = False

    def process_command(self, command: str) -> None:
        if not command:
            return

        # Поиск первой подходящей команды с учетом приоритета
        for keywords, handler in self.command_routes:
            if any(keyword in command for keyword in keywords):
                handler()
                return

        self.speak("Команда не распознана. Скажите 'помощь' для списка команд.")

    def show_help(self) -> None:
        help_text = "Доступные команды: " \
                   "'погода' - информация о погоде, " \
                   "'ветер' - скорость ветра, " \
                   "'направление' - направление ветра, " \
                   "'записать' - сохранить в файл, " \
                   "'прогулка' - рекомендация о прогулке, " \
                   "'выход' - завершить работу."
        self.speak(help_text)

    def run(self) -> None:
        """Главный цикл ассистента"""
        self.speak("Привет! "
                  "Скажите команду или 'помощь'")

        while self.is_running:
            command = self.listen()
            if command:
                self.process_command(command)


if __name__ == "__main__":
    try:
        assistant = WeatherAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\nАссистент завершен пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
