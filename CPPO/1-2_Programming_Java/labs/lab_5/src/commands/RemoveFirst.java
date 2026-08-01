package commands;

import static modules.Collectionr.ticketList;

public class RemoveFirst implements Command {
    final boolean withArg = false;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 0;

    public int getAmountArg() {
        return amountArg;
    }
    public String describe() { return "remove_first - удалить первый элемент из коллекции"; }
    public void execute(String[] text) {
        if (!ticketList.isEmpty()){
            ticketList.removeFirst();
            System.out.println("Удалён первый элемент.");
        }
        else{System.out.println("Коллекция пуста.");}

    }
}
