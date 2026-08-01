package commands;

import modules.EventType;
import modules.Ticket;

import java.util.Iterator;

import static modules.Collectionr.ticketList;

public class RemoveAnyByEvent implements Command {
    final boolean withArg = false;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 3;

    public int getAmountArg() {
        return amountArg;
    }
    public String describe() { return "remove_any_by_event(id, имя, дата в формате yyyy.MM.DD.hh.mm, тип(не обязательно)) " +
            "- удалить из коллекции один элемент, у которого такое же мероприятие"; }
    public void execute(String[] text) {
        int id = Integer.parseInt(text[1]);
        String name = text[2];
        String date = text[3];
        EventType eventType = (text.length==5 ? EventType.fromValue(text[4]):null );
        if(!ticketList.isEmpty()) {
            Iterator<Ticket> iterator = ticketList.iterator();
            int count[]={0};
            while (iterator.hasNext()) {
                Ticket ticket = iterator.next();

                if (ticket.getEvent()==null){
                    continue;
                }
                if ((ticket.getEvent().getIdEvent()==id)&&
                        (ticket.getEvent().getDate().equals(date))&&
                        (ticket.getEvent().getNameEvent().equals(name))&&
                        (ticket.getEvent().getEventType()==eventType)){
                    iterator.remove();
                    count[0]++;
                    break;
                }
            }
            if (count[0]==1){System.out.println("Билет удалён");}
            else{System.out.println("Нет билета с таким мероприятием");}
        }else{System.out.println("Коллекция пуста.");}


    }
}
