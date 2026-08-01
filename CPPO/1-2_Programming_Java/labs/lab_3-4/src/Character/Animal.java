package Character;

import enums.Type;

public abstract class Animal {
    private Type type;
    private String name;
    abstract String action(Object what);

}
