import time
def xml_to_yaml(xml_input):
    # Функция для удаления лишних пробелов и переноса строк
    def clean_text(text):
        return ' '.join(text.split()).strip()
    yaml_output = []
    indent_level = 0
    # Перебираем строки входного XML
    for line in xml_input.splitlines():
        line = clean_text(line)

        if line.startswith('<?xml'):
            continue  # Игнорируем строку с заголовком XML

        if not line:  # Игнорируем пустые строки
            continue

        # Если строка открывающий тег
        if line.startswith('<') and not line.startswith('</'):
            tag_name = line[1:line.find('>')]

            # Добавляем отступы для YAML
            yaml_output.append('  ' * indent_level + f"{tag_name}"+":"+line[line.find(">")+1:line.find("</")])
            indent_level += 1
            if "</"in line: indent_level -=1

        # Если строка закрывающий тег
        elif line.startswith('</'):
            indent_level -= 1

        # Если это текстовый элемент
        else:
            # Извлекаем текстовые данные
            text_value = clean_text(line)
            yaml_output.append('  ' * indent_level + f"- {text_value}n")

    return yaml_output

start_time = time.perf_counter()
# открываем файл
with open('Среда.xml', 'r', encoding= "utf-8") as file:
    xml_file = file.read()
# записываем в другой файл
with open('output0.yaml', 'w', encoding= "utf-8") as file:
    for i in xml_to_yaml(xml_file):
        file.write(i)
# проверка, чисто для себя
print("Всё готово! Проверяйте! Время выполнения:", 100 * (time.perf_counter() - start_time), "   Всё должно быть в файле, но вот пример:")
for i in xml_to_yaml(xml_file):
    print(i)

