import chek.Chek;
import chek.exeptions.FileNotFind;
import commands.*;
import org.xml.sax.SAXException;

import reader.GetNextLine;
import reader.ListReaderFromFile;
//import reader.ReadFromConsole;

import javax.xml.parsers.ParserConfigurationException;
import java.io.IOException;

import static commands.CommandManager.AddCommand;
import static commands.CommandManager.CommandMap;

//IP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.

public class Main {
    public static void main(String[] args) throws IOException, ParserConfigurationException, SAXException {
        String fileName = System.getenv("FILE_NAME");
        //        String path = "C:\\Users\\User\\Desktop\\OneDrive - MSFT\\ИТМО\\Програмирование\\Программы\\Lab_5\\";
        //Загрузка из файла
        ListReaderFromFile.read(fileName);
        //этот метод добавляет команды
        AddCommand();
// хуй0
        while (true) {
            while (true) {
                try {
                    System.out.print("Введите строку: ");
                    //просто берёт строку
                    String line = GetNextLine.getNextLine("console");
                    // чекает, что есть такая команда и нужное кол-во аргументов,
                    // если нет кидает исключения
                    Chek.commandArgument(line);
                    // сюда проходят, если всё хорошо
                    // получаем команду и исполняем её
                    String strCom = line.split(" ")[0];
                    Command command = CommandMap.get(strCom);
                    if (command.getWithArg()) {
                        line += " console";
                    }
                    command.execute(line.split(" "));
                } catch (RuntimeException | FileNotFind e) {
                    System.out.println("Ошибка: " + e.getMessage());
                    System.out.println("Пожалуйста, попробуйте снова.");
                }

                //выполнили команду и выходим из вложенного цикла
                break;
            }
        }
    }
}