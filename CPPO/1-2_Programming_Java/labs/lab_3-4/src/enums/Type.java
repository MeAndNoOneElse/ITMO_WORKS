package enums;

public enum Type {
    DWARF("карлик"),
    PEOPLE("человек"),
    BOY("мальчик"),
    GIANT("великан"),
    PIGS("морские свинки"),
    OLDWOMAN("старуха"),
    SQUIRREL("белка"),
    CHICKEN("курица"),
    CROWD("толпа"),
    MUM("мать");
    private String name;

    Type(String var1) {
        this.name = var1;
    }

    @Override
    public String toString() {
        return name;
    }

    public String getName() {
        return name;
    }
}
