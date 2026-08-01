import xmltodict
import yaml
import time
# Функция для преобразования XML в YAML
def convert_xml_to_yaml(xml_file, yaml_file):
    # Чтение XML файла
    with open(xml_file, 'r', encoding='utf-8') as file:
        xml_content = file.read()

    # Преобразование XML в Python словарь
    dict_data = xmltodict.parse(xml_content)

    # Преобразование словаря в YAML и сохранение в файл
    with open(yaml_file, 'w', encoding='utf-8') as file:
        yaml.dump(dict_data, file, allow_unicode=True, default_flow_style=False)

start_time = time.perf_counter()
# Пример использования функции
xml_file = 'Среда.xml'  # Укажите здесь путь к вашему XML файлу
yaml_file = 'output1.yaml'  # Укажите сюда желаемое имя YAML файла

convert_xml_to_yaml(xml_file, yaml_file)
print("Всё готово! Проверяйте! Время выполнения:" ,  100 * (time.perf_counter() - start_time))
print(f"Преобразование завершено. YAML файл сохранен как: {yaml_file}")
