package commands;

import static modules.Collectionr.ticketList;

/**
 * @author Andrey Anufriev
 * класс для команды clear
 */
public class ClearCommand implements Command {
    final boolean withArg = false;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 0;

    public int getAmountArg() {
        return amountArg;
    }
    /**
     *
     * @return информация о команде
     */
    public String describe() {
        return "clear - очистить коллекцию";
    }

    /**
     *
     * @param text

     * реализует команду clear
     */
    public void execute(String[] text) {
        ticketList.clear();
        if (!ticketList.isEmpty()) {
            System.out.println("Все элементы коллекции удалены.");
        } else {
            System.out.println("Коллекция уже пуста.");
        }

    }
}
