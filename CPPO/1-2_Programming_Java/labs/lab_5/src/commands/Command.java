package commands;

import java.io.IOException;

public interface Command {
    void execute(String[] text) throws IOException;
    String describe();
    boolean getWithArg();
    int getAmountArg();
}
