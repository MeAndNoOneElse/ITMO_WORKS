import enums.Actions;

public record Location(String name) {
    public String filled(Object adj, String how) {
        return (name + " " + Actions.FILLED + " " + adj + " " + how);
    }
}
