package modules;

public enum TicketType {
    VIP("VIP"),
    USUAL("USUAL"),
    BUDGETARY("BUDGETARY"),
    CHEAP("CHEAP");
    private final String name;
    TicketType(String name){
        this.name = name;
    }
    // Геттер для получения значения
    public String getName() {
        return name;
    }

    // Метод для поиска элемента enum по значению
    public static TicketType fromValue(String value) {
        for (TicketType name : TicketType.values()) {
            if (name.equals(value)) {
                return name;
            }
        }
//        throw new IllegalArgumentException("Такого типа билета нет: " + value);
        return null;
    }

    @Override
    public String toString() {
        return getName();
    }
}
//
