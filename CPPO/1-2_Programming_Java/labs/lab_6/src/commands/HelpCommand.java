package commands;

import commands.Command;
import commands.CommandManager;

public class HelpCommand implements Command {
    final boolean withArg = false;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 0;

    public int getAmountArg() {
        return amountArg;
    }
    public String describe() { return "help - помощь"; }
    public void execute(String[] text) {
        System.out.println("Ожидается такой формат: \"команда аргумент аргумент\" возможные аргументы указаны в скобках.\n" +
                "Созданы следующие команды:");
        for (String name : CommandManager.CommandMap.keySet()) {
            String value = CommandManager.CommandMap.get(name).describe();
            System.out.println(value);
        }

        }

    }
