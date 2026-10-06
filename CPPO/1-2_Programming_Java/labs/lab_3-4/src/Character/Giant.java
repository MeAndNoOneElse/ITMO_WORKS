package Character;

import enums.Type;

public class Giant extends Scary {
    private String name;
    private Type type;
    private Object stat;
    private Object location;

    public Giant(String var1, Type var2) {
        this.name = var1;
        this.type = var2;

    }

    @Override
    public void say() {
        System.out.println("Я карлик, меня зовут " + name);
    }

    public Object getLocation() {
        return location;
    }

    public void setLocation(Object location) {
        this.location = location;
    }

    public Object getStat() {
        return stat;
    }

    public void setStat(Object stat) {
        this.stat = stat;
    }

    public String getName() {
        if (Math.random() < 0.5) {
            return name;
        } else {
            return "он";
        }
    }

    public void setType(Type type) {
        this.type = type;
    }

    public Object getType() {
        return type;
    }

    public void setName(String name) {
        this.name = name;
    }

    @Override
    public void action() {

    }
}
