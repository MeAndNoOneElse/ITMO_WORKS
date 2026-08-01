package commands;

import modules.Ticket;

import java.util.Comparator;

import static modules.Collectionr.ticketList;

public class Sort implements Command {
    final boolean withArg = false;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 1;

    public int getAmountArg() {
        return amountArg;
    }
    public String describe() { return "sort(режим)- отсортировать (1-по цене, 2-по id, 3-по алфавиту имени, 4-по длине имени)"; }
    public void execute(String[] text) {
        int x = Integer.parseInt(text[1]);
        switch (x){
            case 1:{
                Comparator<Ticket> priceComparator = Comparator.comparingInt(Ticket::getPrice);
                ticketList.sort(priceComparator);
                System.out.println("Произведена сортировка по цене");
                break;
            }
            case 2:{
                Comparator<Ticket> idComparator = Comparator.comparingLong(Ticket::getId);
                ticketList.sort(idComparator);
                System.out.println("Произведена сортировка по id");
                break;
            }
            case 3:{
                Comparator<Ticket> nameComparator = Comparator.comparing(Ticket::getName);
                ticketList.sort(nameComparator);
                System.out.println("Произведена сортировка по алфавиту имени");
                break;
            }
            case 4:{
                Comparator<Ticket> lengthNameComparator = Comparator.comparingInt(Ticket -> Ticket.getName().length());
                ticketList.sort(lengthNameComparator);
                System.out.println("Произведена сортировка по длине имени");
                break;

            }

        }

    }
}
