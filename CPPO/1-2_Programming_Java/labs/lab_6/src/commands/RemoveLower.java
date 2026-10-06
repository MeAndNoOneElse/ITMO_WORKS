package commands;

import static modules.Collectionr.ticketList;

public class RemoveLower implements Command {
    final boolean withArg = false;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 1;

    public int getAmountArg() {
        return amountArg;
    }
    public String describe() { return "remove_lower(цена) -  удалить из коллекции все элементы, у которых цена меньше, чем заданная"; }
    public void execute(String[] text) {
        int price = Integer.parseInt(text[1]);
        int[] count= {0};
        if (!ticketList.isEmpty()){

            ticketList.removeIf(Ticket -> {
                if (Ticket.getPrice() < price){
                    count[0]+=1;
                    return true;
                }
                return  false;
            });
            System.out.println("Удалено "+count[0]+" билетов");

        }
        else{System.out.println("Коллекция пуста.");}
    }
}
