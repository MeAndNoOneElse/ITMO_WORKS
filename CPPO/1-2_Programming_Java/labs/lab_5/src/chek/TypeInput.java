package chek;

//import modules.Scaner;
import modules.TicketType;
import reader.GetNextLine;

public class TypeInput {
    public static TicketType getAndChekTicketType(String mode) {
        System.out.println("Введите тип билета из списка ниже. Если у Вас нет типа билета, нажмите Enter.");
        System.out.println("Доступные типы билетов:");
        for (TicketType name: TicketType.values()) {
            System.out.println(name.toString().replace("{", "").replace("}", ""));
        }
        TicketType type;

        while (true) {
            String input = GetNextLine.getNextLine(mode).toLowerCase();
            if (input.isEmpty()) {
                System.out.println("Вы уверены, что хотите оставить поле тип билета пустым?(да yes Enter/нет no)");
                String answer = GetNextLine.getNextLine(mode).toLowerCase();
                if (answer.equals("yes")||answer.equals("да")|| answer.isEmpty()) {
                    type = null;
                    return type;
                } else {continue;}
            }
            for (TicketType name: TicketType.values()) {
                if (name.toString().replace("{", "").replace("}", "").equalsIgnoreCase(input)) {
                    type = name;
                    System.out.println("Тип билета успешно принят.");
                    System.out.println();
                    return type;
                }
            }
            System.out.println("Ошибка: введён некорректный тип билета. Попробуйте снова.");
        }
    }
}
