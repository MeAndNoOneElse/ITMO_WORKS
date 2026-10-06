"""
Главный файл для запуска голосовых ассистентов
Лабораторная работа №10
"""

import sys
from pathlib import Path


def print_menu():
    """Показать главное меню"""
    print("\n" + "="*50)
    print("ГОЛОСОВЫЕ АССИСТЕНТЫ - Лабораторная работа №10")
    print("="*50)
    print("1. Ассистент погоды (основное задание)")
    print("   - Информация о погоде в Санкт-Петербурге")
    print("   - Команды: 'погода', 'ветер', 'направление', 'записать', 'прогулка'")
    print("\n2. Ассистент словаря (дополнительное задание)")
    print("   - Поиск слов в английском словаре")
    print("   - Команды: 'find <word>', 'meaning', 'example', 'link', 'save'")
    print("\n0. Выход")
    print("="*50)


def main():
    """Главная функция"""
    while True:
        print_menu()
        choice = input("Выберите опцию (0-2): ").strip()

        if choice == "1":
            print("\nЗапуск ассистента погоды...")
            print("Убедитесь, что микрофон подключен и работает.\n")
            try:
                from voice_weather_assistant import WeatherAssistant
                assistant = WeatherAssistant()
                assistant.run()
            except ImportError:
                print("Ошибка: не удалось загрузить модуль voice_weather_assistant")
            except KeyboardInterrupt:
                print("\nАссистент завершен")
            except Exception as e:
                print(f"Ошибка при запуске ассистента: {str(e)}")

        elif choice == "2":
            print("\nЗапуск ассистента словаря...")
            print("Убедитесь, что микрофон подключен и работает.\n")
            try:
                from voice_dictionary_assistant import DictionaryAssistant
                assistant = DictionaryAssistant()
                assistant.run()
            except ImportError:
                print("Ошибка: не удалось загрузить модуль voice_dictionary_assistant")
            except KeyboardInterrupt:
                print("\nАссистент завершен")
            except Exception as e:
                print(f"Ошибка при запуске ассистента: {str(e)}")

        elif choice == "0":
            print("До свидания!")
            break

        else:
            print("Неверный выбор. Пожалуйста, выберите 0, 1 или 2.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма завершена пользователем")
        sys.exit(0)

