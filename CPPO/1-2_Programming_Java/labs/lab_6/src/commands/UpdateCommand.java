package commands;

import chek.CoordinatesInput;
import chek.EventInput;
import chek.TypeInput;
import modules.Coordinates;
import modules.Event;
import modules.Ticket;
import modules.TicketType;

import java.util.Iterator;

import static modules.Collectionr.ticketList;

public class UpdateCommand implements Command {
    final boolean withArg = false;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 3;

    public int getAmountArg() {
        return amountArg;
    }
    public String describe() { return "update_by_id(id, имя, цена, комментарий(не обязательно) - обновить элемент по его id )"; }
    public void execute(String [] text) {
        if(!ticketList.isEmpty()){
            long id = Long.parseLong(text[1]);
            java.time.LocalDateTime creationDate = null;
            boolean flag = false;
            Iterator<Ticket> iterator = ticketList.iterator();
            while (iterator.hasNext()) {
                Ticket ticket = iterator.next();
                if (id == ticket.getId()){
                    creationDate = ticket.getCreationDate();
                    ticketList.remove(ticket);
                    flag = true;
                    break;
                }
            }
            if (flag){
                //добавляем элемент
                //добавление элемента

                //получаем имя
                String name = text[2];
                //получаем цену
                int price = Integer.parseInt(text[3]);
                //проверка на наличие комментариия
                String comment = null;
                String mode = "";
                if (text.length == 5) {
                    mode = text[4];
                }
                if (text.length == 6){
                    comment = text[4];
                    mode = text[5];
                }

                //А для остальных нужен reader
                //получаем координаты
                Coordinates coordinates = CoordinatesInput.getAndCheckCoordinates(mode);
                //получаем тип
                TicketType type = TypeInput.getAndChekTicketType(mode); //Поле может быть null
                //получаем мероприятие
                Event event = EventInput.getAndChekEvent(mode); //Может быть null

                //создаём билет
                Ticket ticket = new Ticket(id, name, coordinates,creationDate, price, comment, type, event);
                ticketList.add(ticket);
                System.out.println("Билет успешно добавлен!");
            }
            else{
                System.out.println("Нет Билета с таким id");
            }
        }
        else{System.out.println("Коллекция пуста.");}
//обновить значение элемента коллекции, id которого равен заданному
    }
}

