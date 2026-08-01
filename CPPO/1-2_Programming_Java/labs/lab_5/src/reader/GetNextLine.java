package reader;

import java.util.Scanner;

public class GetNextLine {
    /**
     * @param mode
     *
     * @return line в зависимости от режима читает новую строку из сканера или из lines
     */
    public static String getNextLine(String mode, ComReaderFromFile file) {
        String line = null;
        if (mode.equals("console")) {
            Scanner scanner = new Scanner(System.in);
            line = scanner.nextLine().trim();
        }
        if (mode.equals("file")) {
            if (!file.lines.isEmpty()) {
                line = file.lines.get(0);
                file.lines.remove(0);
            }
        }
        return line;
    }
    public static String getNextLine(String mode) {
        String line = null;
        if (mode.equals("console")) {
            Scanner scanner = new Scanner(System.in);
            line = scanner.nextLine().trim();
        }
        return line;
    }
    
    
}