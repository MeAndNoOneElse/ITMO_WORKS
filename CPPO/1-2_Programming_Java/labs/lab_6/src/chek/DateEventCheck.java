package chek;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Date;
import java.util.Scanner;

public class DateEventCheck {
    public static Date chekDate() {
        Scanner scanner = new Scanner(System.in);
        LocalDateTime eventDate = null;
        System.out.println("Введите дату мероприятия в формате yyyy.MM.dd.HH.mm:");
        while (eventDate == null) {
            String dateString = scanner.nextLine().trim();
            try {
                // Парсим строку в LocalDateTime
                eventDate = LocalDateTime.parse(dateString, DateTimeFormatter.ofPattern("yyyy.MM.dd.HH.mm"));

                // Проверяем, что дата существует (например, 31 февраля не существует)
                if (!isValidDateTime(eventDate)) {
                    System.out.println("Ошибка: введённая дата не существует. Пожалуйста, введите корректную дату.");
                    eventDate = null; // Сбрасываем дату, чтобы цикл продолжился
                    continue;
                }

                // Проверяем, что дата находится в будущем
                LocalDateTime now = LocalDateTime.now();
                if (eventDate.isBefore(now)) {
                    System.out.println("Ошибка: введённая дата должна быть в будущем. Пожалуйста, введите дату позже текущего времени.");
                    eventDate = null; // Сбрасываем дату, чтобы цикл продолжился
                }

            } catch (DateTimeParseException e) {
                System.out.println("Ошибка: некорректный формат даты. Пожалуйста, введите дату в формате 'yyyy.MM.dd.HH.mm'.");
            }
        }

        System.out.println("Дата мероприятия успешно добавлена: " + eventDate);

        ZonedDateTime zonedDateTime = eventDate.atZone(ZoneId.systemDefault());

        // Преобразуем ZonedDateTime в Instant
        Instant instant = zonedDateTime.toInstant();
        return Date.from(instant);
    }

    /**
     * Проверяет, что введённая дата существует (например, 31 февраля не существует).
     */
    public static boolean isValidDateTime(LocalDateTime dateTime) {
        try {
            // Если дата корректна, метод ничего не выбросит
            dateTime.getYear(); // Проверка года
            dateTime.getMonthValue(); // Проверка месяца (1-12)
            dateTime.getDayOfMonth(); // Проверка дня (1-31, в зависимости от месяца и года)
            dateTime.getHour(); // Проверка часов (0-23)
            dateTime.getMinute(); // Проверка минут (0-59)
            return true;
        } catch (Exception e) {
            return false; // Если дата некорректна
        }
    }

}
