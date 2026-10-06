package commands;

import modules.Ticket;

import java.text.SimpleDateFormat;

import static modules.Collectionr.ticketList;
import  reader.ListReaderFromFile;

public class InfoCommand implements Command {
    final boolean withArg = false;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 0;

    public int getAmountArg() {
        return amountArg;
    }
    public String describe() { return "info - информация о коллекции"; }
    public void execute(String[] text) {
        System.out.println("Тип коллекции: "+ ticketList.getClass().getSimpleName());
        System.out.println("Тип элементов коллекции: "+Ticket.class.getSimpleName());

        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy.MM.dd HH:mm:ss");
        System.out.println("Дата инициализации: " + dateFormat.format(ListReaderFromFile.getInitializationDate()));
        System.out.println("Количество элементов: " + ticketList.size());
        if (!ticketList.isEmpty()) {
            System.out.println("Первый элемент: " + ticketList.getFirst());
            System.out.println("Последний элемент: " + ticketList.getLast());
        }

    }
}
