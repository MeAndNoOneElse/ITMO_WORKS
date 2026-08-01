import re
import time
def xml_to_yaml(xml):
    s = xml.read()
    s = re.sub('    ', '', s)

    s = re.sub(r'(?:</.*>)|(?:<\?.*\?>)|<', '', s)
    s = re.sub('>', ':', s)
    #s = re.sub('lesson:', 'lesson:', s)
    s = re.sub(r'^s*lesson:', '  lesson:', s, flags=re.MULTILINE)
    s = re.sub(r'^s*\n$', '', s, flags=re.MULTILINE)
    s = re.sub(r' {2,}', ' ', s, flags=re.MULTILINE)
    s = re.sub('^\n', '', s, flags=re.MULTILINE)
    s = re.sub(r'^\s*\n', '', s, flags=re.MULTILINE)
    YAML.write(s)

start_time = time.perf_counter()
XML = open("Среда.xml", mode="r", encoding="utf-8")
YAML = open("output2.yaml", mode="w", encoding="utf-8")
xml_to_yaml(XML)
XML.close()
YAML.close()
print("Всё готово! Проверяйте! Время выполнения:", 100 * (time.perf_counter() - start_time))
