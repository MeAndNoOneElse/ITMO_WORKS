package commands;

import chek.*;
import modules.*;

import static modules.Collectionr.ticketList;

/**
 * @author Andrey Anufriev
 * класс для реализации add_if_max
 */
public class AddIfMaxCommand implements Command {
    final boolean withArg = true;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 2;

    public int getAmountArg() {
        return amountArg;
    }

    /**
     *
     * @return информация о команде
     */
    public String describe() {
        return "add_if_max(имя, цена, комментарий(не обязательно)) - добавить элемент, если его цена больше всех";
    }

    /**
     *
     * @param text
     * реализует команду add_if_max
     */
    public void execute(String[] text) {
        int price = Integer.parseInt(text[2]);
        if (!ticketList.isEmpty()) {
            int maxPrice = 0;
            for (Ticket ticket : ticketList) {
                if (ticket.getPrice() > maxPrice) {
                    maxPrice = ticket.getPrice();
                }
            }
            if (price > maxPrice) {
                //добавление элемента
                //генерится id
                long id = Generation.getLongID();
                //получаем имя
                String name = text[1];
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
            } else {
                System.out.println("Элемент не добавлен, введёная цена не максимальна");
            }
        } else {
            System.out.println("Коллекция пуста");
        }
//добавить новый элемент в коллекцию, если его значение превышает значение наибольшего элемента этой коллекции
    }
}
