package enums;

public enum Adject {
    LONG("длинный"),
    FUNNY("смешно"),
    BLACK("черный"),
    DIRECT("прямо"),
    UGLY_I("безобразн"),//инфинитив
    UGLY("безобразные"),
    OTHER("другое"),
    STRANGE("странные"),
    VERY("очень");

    private String name;

    Adject(String var1) {
        this.name = var1;
    }

    @Override
    public String toString() {
        return name;
    }
}

