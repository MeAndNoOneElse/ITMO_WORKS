package enums;

public enum Sign {
    DOT("."),
    EX("!"),
    QU("?"),
    COLON(":"),
    DASH("-"),
    COMMA(",");
    private String name;

    Sign(String var1) {
        this.name = var1;
    }

    @Override
    public String toString() {
        return name;
    }
}
