package chek;

import modules.Event;
import modules.EventType;
//import modules.Scaner;
import reader.GetNextLine;

import java.util.Date;

public class EventInput {
    public static Event getAndChekEvent(String mode) {


        Event event;
    //Выясняем будет ли чел заполнять поля мероприятия
        while (true) {
            System.out.println("Вы будете заполнять информацию о мероприятие? (да yes Enter/хоть что)");
            String answer = GetNextLine.getNextLine(mode).toLowerCase();
            if (!answer.equals("yes") & !answer.equals("да") & !answer.equals("")) {
                System.out.println("Вы действительно хотите оставить поле event пустым и завершить создание билета? (да yes Enter/хоть что)");
                String answer2 = GetNextLine.getNextLine(mode).toLowerCase();
                if (answer2.equals("yes") || answer2.equals("да")|| answer2.equals("")) {
                    event = null;
                    return event;
                }
            }
            else{break;}

        }

        // Запрашиваем имя мероприятия

        String nameEvent = null;
        System.out.println("Введите имя мероприятия. Это обязательное поле, оно не может быть пустым:");
        while (nameEvent == null || nameEvent.isEmpty()) {
            nameEvent = GetNextLine.getNextLine(mode);
            if (nameEvent.isEmpty()) {
                System.out.println("Ошибка: имя мероприятия не может быть пустым.");
            }
        }
        System.out.println("Название мероприятия успешно добавлено.");
        System.out.println();
        // Запрашиваем дату мероприятия
        Date date = DateEventCheck.chekDate();
//        System.out.println("Введите дату мероприятия в формате yyyy.MM.dd.HH.mm:");
//        String dateString = scanner.nextLine().trim();
//        while (date == null) {
//            String dateString = scanner.nextLine().trim();
//            try {
//                // Парсим строку в Date (используем SimpleDateFormat)
//                date = new SimpleDateFormat("yyyy.MM.dd.HH.mm").parse(dateString);
//            } catch (Exception e) {
//                System.out.println("Ошибка: некорректный формат даты. Пожалуйста, введите дату в формате 'yyyy-MM-dd HH:mm:ss'.");
//            }
//        }
//        System.out.println("Дата мероприятия успешно добавлена.");
//        System.out.println();

        // Запрашиваем тип мероприятия

        EventType eventType = null;
        System.out.println("Доступные типы билетов:");
        for (EventType name: EventType.values()) {
            System.out.println(name.toString().replace("{", "").replace("}", ""));
        }
        flag: while (true) {
            System.out.println("Введите тип мероприятия из списка выше. Если у Вас нет типа билета, нажмите Enter.");

            String input = GetNextLine.getNextLine(mode).toLowerCase();
            if (input.isEmpty() || input.equals("null") || input.equals("")) {
                System.out.println("Вы уверены, что хотите оставить поле тип билета пустым?(да yes Enter/нет no)");

                String answer3 = GetNextLine.getNextLine(mode).toLowerCase();
                if (answer3.equals("yes") || answer3.equals("да") || answer3.equals("")) {
                    eventType = null;
                    break flag;
                } else {
                    continue flag;
                }
            }
            for (EventType name: EventType.values()) {
                if (name.toString().replace("{", "").replace("}", "").equalsIgnoreCase(input)) {
                    eventType = name;
                    System.out.println("Тип мероприятия успешно принят.");
                    System.out.println();
                    break flag;
                }
            }
            System.out.println("Ошибка: введён некорректный тип мероприятия. Попробуйте снова.");
        }
        int idEvent = Generation.getIntID();
        event = new Event(idEvent, nameEvent, date, eventType);
        return event;
    }

}
