package commands;

import modules.Ticket;

import static modules.Collectionr.ticketList;

public class ShowCommand implements Command {
    final boolean withArg = false;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 0;

    public int getAmountArg() {
        return amountArg;
    }
    public String describe() { return "show - выводит все элементы коллекции"; }
    public void execute(String[] text) {
        if (!ticketList.isEmpty()) {
            for (Ticket ticket: ticketList){
                System.out.println(ticket.toString());
            }
        }
        else {System.out.println("Коллекция пуста");}
    //: вывести в стандартный поток
        // вывода все элементы коллекции в строковом представлении
    }
}
