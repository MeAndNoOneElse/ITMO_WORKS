package commands;

import commands.Command;

public class ExitCommand implements Command {
    final boolean withArg = false;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 0;

    public int getAmountArg() {
        return amountArg;
    }
    boolean witharg;

    public String describe() {
        return "exit - выход из программы без сохранения"; }
    public void execute(String[] text) {
        System.exit(0);
    }
}
