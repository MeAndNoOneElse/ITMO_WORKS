package modules;

import java.time.LocalDateTime;

public class Ticket {
    private long id; //Значение поля должно быть больше 0, Значение этого поля должно быть уникальным, Значение этого поля должно генерироваться автоматически
    private  String name; //Поле не может быть null, Строка не может быть пустой
    private Coordinates coordinates; //Поле не может быть null
    private java.time.LocalDateTime creationDate; //Поле не может быть null, Значение этого поля должно генерироваться автоматически
    private int price; //Значение поля должно быть больше 0
    private String comment; //Поле может быть null
    private TicketType type; //Поле может быть null
    private Event event; //Поле может быть null

    public Ticket (long id, String name, Coordinates coordinates,
                   LocalDateTime creationDate, int price, String comment,
                   TicketType type, Event event){
        this.id= id;
        this.name = name;
        this.coordinates = coordinates;
        this.creationDate = creationDate;
        this.price = price;
        this.comment = comment;
        this.type = type;
        this.event = event;
    }
    @Override
    public String toString() {
        return "Ticket id:" + id+", название:" + name +
                ", цена:" + price +
                (comment != null ? ", комментарий:" + comment: "") +
                ",\n\t координаты:" + coordinates.toString() +
                ", дата создания:" + creationDate +
                (type != null ? ", \n\t тип:" + type.toString():"") +
                (event != null ? ", \n\t мероприятие:\n\t\t" +event.toString():"");
    }

    public int getPrice() {
        return price;
    }

    public long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public Coordinates getCoordinates() {
        return coordinates;
    }


    public LocalDateTime getCreationDate() {
        return creationDate;
    }

    public String getComment() {
        return comment;
    }

    public Event getEvent() {
        return event;
    }

    public TicketType getType() {
        return type;
    }

}

