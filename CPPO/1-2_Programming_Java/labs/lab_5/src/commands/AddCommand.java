package commands;

import chek.*;
import modules.*;

import static modules.Collectionr.ticketList;

/**
 * @author Andrey Anufriev
 * "класс для реализации add"
 */
public class AddCommand implements Command { // Add Command
    final boolean withArg = true;
    final int amountArg = 2;

    public int getAmountArg() {
        return amountArg;
    }

    public boolean getWithArg() {
        return withArg;
    }

    /**
     *
     * @return "информация о команде"
     */
    public String describe() {
        return "add(имя, цена, комментарий(не обязательно)) - добавить ";
    }

    /**
     *
     * @param text
     * реализует команду add
     */
    public void execute(String[] text) {

        //генерится id
        long id = Generation.getLongID();
        //получаем имя
        String name = text[1];
        //получаем цену
        int price = Integer.parseInt(text[2]);
        //проверка на наличие комментариия
        String comment = null;
        String mode = "";
        if (text.length == 4) {
            mode = text[3];
        }
        if (text.length == 5) {
            comment = text[3];
            mode = text[3];
        }
        System.out.println("Начато создание билета id:" + id + " имя:" + name + " цена:" + price + (comment == null ? "" : " комментарий: " + comment));
        // генерим дату
        java.time.LocalDateTime creationDate = Generation.getCreationDate();

        //А для остальных нужен reader
        //получаем координаты
        Coordinates coordinates = CoordinatesInput.getAndCheckCoordinates(mode);
        //получаем тип
        TicketType type = TypeInput.getAndChekTicketType(mode); //Поле может быть null
        //получаем мероприятие
        Event event = EventInput.getAndChekEvent(mode); //Может быть null

        //создаём билет
        Ticket ticket = new Ticket(id, name, coordinates, creationDate, price, comment, type, event);
        ticketList.add(ticket);
        System.out.println("Билет успешно добавлен!");
    }
}