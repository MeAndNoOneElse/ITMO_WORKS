package modules;

import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Date;

public class Event {
    private  int idEvent; //Значение поля должно быть больше 0, Значение этого поля должно быть уникальным, Значение этого поля должно генерироваться автоматически
    private  String nameEvent; //Поле не может быть null, Строка не может быть пустой
    private  java.util.Date date; //Поле не может быть null
    private  EventType eventType; //Поле может быть null

    public Event(int id, String name, java.util.Date date, EventType eventType ){
        this.idEvent = id;
        this.nameEvent = name;
        this.date = date;
        this.eventType = eventType;
    }

    public  String getNameEvent() {
        return nameEvent;
    }
    public  EventType getEventType() {
        return eventType;
    }
    public  int getIdEvent(){
        return idEvent;
    }
    public String getDate() {
        return new SimpleDateFormat("yyyy.MM.dd.HH.mm").format(date);
    }

    @Override
    public String toString() {
        return "id:"+getIdEvent()+", имя:"+getNameEvent()+
                ", дата:"+getDate()+
                (getEventType() != null ? ", тип:"+getEventType().toString(): "");
    }
}
