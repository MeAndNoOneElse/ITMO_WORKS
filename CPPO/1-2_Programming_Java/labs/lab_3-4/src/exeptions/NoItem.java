package exeptions;

public class NoItem extends Exception {

    @Override
    public String getMessage() {
        return "!!!Error NoItems: " + super.getMessage();
    }
}
