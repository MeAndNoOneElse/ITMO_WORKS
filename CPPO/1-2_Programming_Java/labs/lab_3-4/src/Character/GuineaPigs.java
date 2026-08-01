package Character;

import enums.Type;

public class GuineaPigs extends Animal {
    private final Type type;
    private String name;

    public GuineaPigs(String name, Type type) {
        this.name = name;
        this.type = type;
    }


    @Override
    public String action(Object what) {
        return (type + " зажгли " + what);
    }

    public String getName() {
        return name;
    }

    public Type getType() {
        return type;
    }


}
