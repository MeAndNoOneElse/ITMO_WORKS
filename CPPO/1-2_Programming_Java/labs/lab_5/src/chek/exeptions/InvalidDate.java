package chek.exeptions;

public class InvalidDate extends IllegalArgumentException {
    public InvalidDate(String message) {
        super(message);
    }
}
