package enums;

public enum BodPar {
    HAND("руки"),
    NOSE("нос"),
    HEAD("голова"),
    FOOT("ноги"),
    NECK("шею"),
    FEATHERS("перья"),
    LEATHER("кожу"),
    ENTRAILS("внутренности"),
    ALL("всё тело"),//всё тело
    SHOULDER("плечах");
    private String name;
    BodPar(String var1){
        this.name = var1;
    }
    @Override
    public String toString(){
        return name;
    }
}

