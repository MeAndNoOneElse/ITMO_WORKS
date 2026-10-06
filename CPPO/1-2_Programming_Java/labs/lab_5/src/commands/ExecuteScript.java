package commands;

import chek.Chek;
import chek.exeptions.*;

import reader.ComReaderFromFile;
import reader.GetNextLine;

import java.io.IOException;
import java.util.ArrayList;


import static commands.CommandManager.CommandMap;

/**
 * @author Andrey Anufriev
 */
public class ExecuteScript implements Command {
    final boolean withArg = false;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 1;

    public int getAmountArg() {
        return amountArg;
    }
    ArrayList<String> filePaths = new ArrayList<>();

    public String describe() {
        return "execute_script(имя файла) - исполнить скрипт из указанного файла";
    }

    public void execute(String[] text) throws IOException {
        String fileName = text[1];
        if (! filePaths.contains(fileName)) {
            filePaths.add(fileName);
        } else {
            throw new HaveRecoursion("Произошла рекурсия в файле:" + filePaths.get(filePaths.size() - 1));

        }
        ComReaderFromFile awer = new ComReaderFromFile();

        awer.read(fileName);
        flag:
        while (true) {
            while (true) {
                String line;
                if (! awer.getLines().isEmpty()) {
                    line = GetNextLine.getNextLine("file", awer);
                } else {
                    System.out.println("Скрипт:" + fileName + " исполнен");
                    break flag;
                }
                try {
                    Chek.commandArgument(line);
                    String strCom = line.split(" ")[0];
                    Command command = CommandMap.get(strCom);
                    if (command.getWithArg()) {
                        line += " file";
                    }
                    command.execute(line.split(" "));
                    break;
                } catch (InvalidDate | InvalideTicketType | MoreFieldException | InvalidIDExeption | InvalidCoordinate |
                         InvalidCommandExeption | InvalidNameException | InvalidPriceException | MissingFieldException |
                         FileNotFind e) {
                    System.out.println("Ошибка: " + e.getMessage());
                    System.out.println("Пожалуйста, попробуйте снова.");
                }
            }
        }
        // Восстанавливаем предыдущее состояние


    }
}
