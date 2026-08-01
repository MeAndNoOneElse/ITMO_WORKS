package chek;

import modules.Coordinates;
import reader.GetNextLine;

public class CoordinatesInput {
    public static Coordinates getAndCheckCoordinates(String mode){
        double x;
        float y;
        System.out.println("Введите координаты через пробел X и Y. (Обе координаты обязательные, Y должен быть больше -121)");

        while (true) {
            try {
                //получаем строку и парсим
                String[] arguments = GetNextLine.getNextLine(mode).split(" ");
                // проверка на кол-во чисел
                if (arguments.length!=2){
                    System.out.println("Ошибка ввода: неверное кол-во аргументов. Введите 2 числа через пробел.");
                continue;
                }

                //получаем X
                x = Double.parseDouble(arguments[0]);
                // получаем Y
                y = Float.parseFloat(arguments[1]);
                if (y <= -121) {
                    System.out.println("Ошибка ввода: координата Y должна быть больше -121.");
                    continue;
                }
                break;
            }
            catch (NumberFormatException e) {
                System.out.println("Ошибка ввода: введены некорректные числа. Введите ЧИСЛА в правильном формате.");
            }
        }
        System.out.println("Coordinates принята. ("+x+"; "+y+")");
        return new Coordinates(x, y);
    }

}
