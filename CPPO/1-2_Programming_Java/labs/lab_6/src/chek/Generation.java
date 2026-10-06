package chek;

import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.UUID;

public class Generation {
    public static HashSet<Long> LongID = new HashSet<Long>();
    public static HashSet<Integer> IntID = new HashSet<Integer>();

    // генерация уникального id long для билетов
    public static long getLongID() {
        long id;
        while (true) {
            id = Math.abs(UUID.randomUUID().getLeastSignificantBits());
            if (!(LongID.contains(id))) {
                LongID.add(id);
                break;
            }
        }
        return id;
    }
    //Генерация уникального id int для мероприятий
    public static int getIntID() {
        int id;
        while (true) {
            id = (int) (Math.random() * Integer.MAX_VALUE);
            if (!(IntID.contains(id))) {
                IntID.add(id);
                break;
            }
        }
        return id;
    }
    // генерация текущего времени creationDate
    public static LocalDateTime getCreationDate() {
        return LocalDateTime.now();
    }
}
