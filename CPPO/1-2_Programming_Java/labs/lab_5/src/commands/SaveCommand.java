package commands;

import modules.Ticket;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

import static modules.Collectionr.ticketList;

public class SaveCommand implements Command {
    final boolean withArg = false;

    public boolean getWithArg() {
        return withArg;
    }
    final int amountArg = 0;

    public int getAmountArg() {
        return amountArg;
    }
    public String describe() { return "save - сохранить коллекцию в новый файл с именем текущей даты"; }
    public void execute(String[] text) {
        // Создание файла
        String DateTime = LocalDateTime.now().format(DateTimeFormatter.ofPattern("MM.dd.HH.mm.ss"));
        String fileName = "LastSave_"+DateTime+".xml";
        // Создание файла

        File file = new File(fileName);
        // Запись
        try (FileWriter writer = new FileWriter(file)){
            writer.write("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n");
            //Основной блок записи пробегаем по полям элемента и форматируем вывод toString
            writer.write("<Tickets>\n");
            for (Ticket ticket: ticketList) {
                writer.write("\t<Ticket>\n");
                writer.write("\t\t<id>"+(ticket.getId())+"</id>\n");
                writer.write("\t\t<name>"+(ticket.getName())+"</name>\n");
                writer.write("\t\t<price>"+(ticket.getPrice())+"</price>\n");
                writer.write("\t\t<coordinates>\n");
                writer.write("\t\t\t<X>"+(ticket.getCoordinates().getX())+"</X>\n");
                writer.write("\t\t\t<Y>"+(ticket.getCoordinates().getY())+"</Y>\n");
                writer.write("\t\t</coordinates>\n");
                writer.write("\t\t<creationDate>"+(ticket.getCreationDate())+"</creationDate>\n");
                if (ticket.getComment() != null) {
                    writer.write( "\t\t<comment>"+ticket.getComment()+"</comment>\n");
                }
                if (ticket.getType() != null) {
                    writer.write( "\t\t<type>"+ticket.getType().toString().replace("{", "").replace("}", "")+"</type>\n");
                }
                if (ticket.getEvent() != null) {
                    writer.write("\t\t<event>\n");
                    writer.write( "\t\t\t<idEvent>"+ticket.getEvent().getIdEvent()+"</idEvent>\n");
                    writer.write( "\t\t\t<nameEvent>"+ticket.getEvent().getNameEvent()+"</nameEvent>\n");
                    writer.write( "\t\t\t<date>"+ticket.getEvent().getDate()+"</date>\n");
                    if (ticket.getEvent().getEventType() != null) {
                        writer.write( "\t\t\t<eventType>"+ticket.getEvent().getEventType().toString().replace("{", "").replace("}", "")+"</eventType>\n");
                    }
                    writer.write("\t\t</event>\n");
                }
                writer.write("\t</Ticket>\n");
            }
            writer.write("</Tickets>");
            writer.flush();
            System.out.println("Билеты успешно записаны в файл.");
        } catch (IOException e) {

            System.out.println("Ошибка при записи в файл: "+ e.getMessage());
            e.printStackTrace();
            throw new RuntimeException("Ошибка при записи в файл", e);
        }


        //сохранить коллекцию в файл
    }
}
