package commands;

import modules.EventType;
import modules.Ticket;

import java.util.Iterator;

import static modules.Collectionr.ticketList;

public class RemoveAllByEvent implements Command {
    final boolean withArg = false;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 2;

    public int getAmountArg() {
        return amountArg;
    }
    public String describe() {
        return "remove_all_by_event(имя, дата в формате yyyy.MM.DD.hh.mm, тип(не обязательно)) - удалить из коллекции все элементы, у которых такое же мероприятие";
    }

    public void execute(String[] text)  {
        String name = text[1];
        String date = text[2];
        EventType eventType = (text.length==4 ? EventType.fromValue(text[3]):null );
        if(!ticketList.isEmpty()) {
            int count=0;
            Iterator<Ticket> iterator = ticketList.iterator();
            while (iterator.hasNext()) {
                Ticket ticket = iterator.next();

                if (ticket.getEvent()==null){
                    continue;
                }
                if ((ticket.getEvent().getDate().equals(date))&&
                        (ticket.getEvent().getNameEvent().equals(name))&&
                        (ticket.getEvent().getEventType()==eventType)){
                    iterator.remove();
                    count++;
                }
            }
            System.out.println("Удалено "+count+" билетов");
        }else{System.out.println("Коллекция пуста.");}
    }
}