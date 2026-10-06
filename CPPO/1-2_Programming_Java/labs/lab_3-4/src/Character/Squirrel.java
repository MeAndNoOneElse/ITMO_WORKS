package Character;

import enums.Type;

public class Squirrel extends Animal {
    private final Type type;
    private final String name;

    @Override
    public String action(Object var1) {
        return "Привет";
    }

    public Squirrel(String name, Type type) {
        this.name = name;
        this.type = type;
    }

    public String getName() {
        return name;
    }

    public Type getType() {
        return type;
    }

    public String bake(Object var) {
        return ("ей пекли хлеб исключительно из " + var);
    }
}
