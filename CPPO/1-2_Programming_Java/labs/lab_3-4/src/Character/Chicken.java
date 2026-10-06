package Character;

import enums.Type;

public class Chicken extends Animal{
    private Type type;
    private String name;
    @Override
    public String action(Object var1){
        return "Ко-ко-ко";
    }
    public Chicken(String name){
        this.name = name;
        this.type = Type.CHICKEN;}
    public String getName(Integer x){
        return switch (x) {
            case 1 -> "она";
            case 2 -> "ей";
            case 3-> "её";
            case 4 ->"неё";
            default ->name;
        };
    }
    public Type getType(){
        return type;
    }
}
