package commands;

import modules.Ticket;

import java.util.Iterator;

import static modules.Collectionr.ticketList;

public class RemoveById implements Command {
    final boolean withArg = true;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 1;

    public int getAmountArg() {
        return amountArg;
    }
    public String describe() { return "remove_by_id(id) - удалить элемент по id  "; }
    public void execute(String[] text) {
        long id = Long.parseLong(text[1]);
        boolean flag = false;
        if (!ticketList.isEmpty()){
            Iterator<Ticket> iterator = ticketList.iterator();
            while (iterator.hasNext()) {
                Ticket ticket = iterator.next();
                if (id == ticket.getId()){
                    ticketList.remove(ticket);
                    flag = true;
                    System.out.println("Билет удалён");
                    break;
                }
            }
            if (!flag){
                System.out.println("Билета с таким id нет");
            }
        }else {System.out.println("Коллекция пуста.");}

//удалить элемент из коллекции по его id
    }
}
