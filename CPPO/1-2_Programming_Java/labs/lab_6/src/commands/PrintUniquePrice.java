package commands;

import modules.Ticket;

import java.util.HashSet;

import static modules.Collectionr.ticketList;

public class PrintUniquePrice implements Command {
    final boolean withArg = false;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 0;

    public int getAmountArg() {
        return amountArg;
    }
    public String describe() { return "print_unique_price - вывести уникальные цены"; }
    public void execute(String[] text) {
        if (!ticketList.isEmpty()){
            // Создаем HashSet для хранения уникальных цен
            HashSet<Integer> uniquePrices = new HashSet<>();
            // Проходим по всем элементам коллекции и добавляем цены в HashSet
            for (Ticket ticket : ticketList) {
            uniquePrices.add(ticket.getPrice());
            }
            System.out.println("Уникальные цены: ");
            for (int price :uniquePrices){
            System.out.println(price);
            }
        }
        else{System.out.println("Коллекция пуста.");}

    }
}
