def parse_xml(filename):
    data = []
    with open(filename, 'r', encoding='windows-1251') as file:
        row = []
        for line in file:
            if "<Valute ID=" in line:  # <Valute ID="R01010">
                ID = line.replace('<Valute ID="', "").replace('">', "").replace(" ", "").replace("\n", "")
                row.append(ID)
            if "NumCode" in line:
                NumCode = int(
                    line.replace("<NumCode>", "").replace("</NumCode>", "").replace(" ", "").replace("\n", ""))
                row.append(NumCode)
            if "<CharCode>" in line:  # <CharCode>AUD</CharCode>
                CharCode = line.replace("<CharCode>", "").replace("</CharCode>", "").replace(" ", "").replace("\n", "")
                row.append(CharCode)
            if len(row) != 0 and (len(row)) % 3 == 0:
                data.append(row)
                row = []
    return data


def create_NumCode_list(data):
    NumCodeList = []
    for row in data:
        NumCodeList.append([row[0], row[1]])
    with open('NumCodeList.txt', 'w', encoding='utf-8') as f:
        for row in NumCodeList:
            f.write(f"{row}\n")
    print("Создан список NumCodeList в одноимённом файле")
    return NumCodeList


def create_CharCode_list(data):
    CharCodeList = []
    for row in data:
        CharCodeList.append([row[0], row[2]])
    with open('CharCodeList.txt', 'w', encoding='utf-8') as f:
        for row in CharCodeList:
            f.write(f"{row}\n")
    print("Создан список CharCodeList в одноимённом файле")
    return CharCodeList


# print(*parse_xml("currency.xml"), sep="\n")
print(*create_NumCode_list(parse_xml("currency.xml")), sep="\n")
print(*create_CharCode_list(parse_xml("currency.xml")), sep="\n")
