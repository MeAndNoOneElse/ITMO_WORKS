package chek.exeptions;

public class InvalideTicketType extends IllegalArgumentException {
    public InvalideTicketType(String message) {
        super(message);
    }
}
