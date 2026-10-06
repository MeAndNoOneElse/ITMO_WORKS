package Character;

import enums.Type;

public class Group implements People {
    private String name;
    private enums.Type Type;

    public void setType(Type type) {
        Type = type;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public Object getType() {
        return Type;
    }

    public Group(String name, Type Type) {
        this.name = name;
        this.Type = Type;
    }

    public Group(String name) {
        this.name = name;

    }

    @Override
    public void action() {

    }

    @Override
    public void say() {
        System.out.println("Привет");
    }
}
