package Character;

import enums.Type;

public class MC_Mum extends Characters {
    private final String name;
    private final Type type;

    public MC_Mum(String name) {
        this.name = name;
        this.type = Type.MUM;
    }

    @Override
    public void say() {
        System.out.println("привет, меня зовут " + name + ". Я главный герой");
    }

    @Override
    public void action() {
    }

    public String sat() {
        return getType() + " все еще сидела на своем месте";
    }

    public String turn() {
        return type + " обернулась, но в ту же минуту отшатнулась от него с криком ужаса";
    }

    public String said(Object var) {
        return var + "";
    }

    @Override
    public String getName(Integer x) {
        return switch (x) {
            case 1 -> "она";
            case 2 -> "ей";
            case 3 -> "её";
            case 4 -> "неё";
            default -> name;
        };
    }

    public Type getType() {
        return type;
    }
}
