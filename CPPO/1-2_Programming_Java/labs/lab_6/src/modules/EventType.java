package modules;

public enum EventType {
    E_SPORTS("E_SPORTS"),
    BASEBALL("BASEBALL"),
    BASKETBALL("BASKETBALL"),
    THEATRE_PERFORMANCE("THEATRE_PERFORMANCE");
    private final String name;
    EventType(String name){
        this.name = name;
    }
    // Геттер для получения значения
    public String getName() {
        return name;
    }

    @Override
    public String toString() {
        return getName();
    }

    // Метод для поиска элемента enum по значению
    public static EventType fromValue(String value) {
        for (EventType name : EventType.values()) {
            if (name.getName().equals(value)) {
                return name;
            }
        }
        //throw new IllegalArgumentException("Такого типа ивента нет: " + value);

        return null;
    }
}
