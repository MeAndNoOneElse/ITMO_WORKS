package chek.exeptions;

import java.io.FileNotFoundException;

public class FileNotFind extends FileNotFoundException {
    public FileNotFind(String message) {
        super(message);
    }
}
