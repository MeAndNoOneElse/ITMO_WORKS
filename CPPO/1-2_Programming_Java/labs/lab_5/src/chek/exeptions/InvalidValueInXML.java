package chek.exeptions;

import java.io.IOException;

public class InvalidValueInXML extends IOException {
    public InvalidValueInXML(String message) {
        super(message);
    }
}
