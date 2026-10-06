package Character;

import enums.*;

public class Dwarf extends Scary {
    private String name;
    private String appearance;
    private Object type;
    private Object stat;
    private Object location;
    private final int Dec;

    public Dwarf(String var1, int var4, String var2, Object var3) {
        this.name = var1;
        this.appearance = var2;
        this.type = var3;
        this.Dec = var4;

    }

    public int getDec() {
        return Dec;
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

    public String getName2() {
        return "него";
    }

    public void setType(Type type) {
        this.type = type;
    }

    public Object getType() {
        return type;
    }

    @Override
    public String toString() {
        return this.toString();
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getAppearance() {
        return appearance;
    }

    public void setAppearance(String name) {
        this.appearance = name;
    }

    @Override
    public void action() {
    }

    public void exist() {
        System.out.println("Появился карлик. Его зовут " + name + ".");
    }
}
