//package chek;
//
//
//import chek.exeptions.*;
//import commands.Command;
//import commands.CommandManager;
//import reader.GetNextLine;
//
//import java.io.File;
//
//public abstract class ChekArgCommand {
//    /**
//     *
//     * @param input
//     * @throws InvalidCommandExeption
//     * @throws InvalidNameException
//     * @throws InvalidPriceException
//     * @throws MissingFieldException
//     * чекает корректность введённой строки с командой
//     */
//    public static void read(String input) throws InvalidCommandExeption, InvalidNameException, InvalidPriceException, MissingFieldException, FileNotFind {
//        String[] token = input.split(" ");
//        // Проверка на минимальное количество элементов
//        if (token.length == 0) {
//            throw new MissingFieldException("Введенная строка пуста.");
//        }
//        String strcommand = token[0];
//
//        // Проверка на валидность команды
//        if (!CommandManager.CommandMap.containsKey(strcommand)) {
//            throw new InvalidCommandExeption("Неверная команда: " + strcommand);
//        }
//        //Определение команды
//        Command command = CommandManager.CommandMap.get(strcommand);
//        //далее нам надо определить сколько аргументов нужно для команды
//        //не требуется аргументов для: help info show clear save exit
//        // remove_first print_unique_price
//        //на этом проверка заканчивается и можно выполнять команду
//        if (strcommand.equals("save") || strcommand.equals("clear") || strcommand.equals("info")
//                || strcommand.equals("show") || strcommand.equals("exit") || strcommand.equals("help")||
//                strcommand.equals("print_unique_price")|| strcommand.equals("remove_first")){
//            if (token.length>=2){
//                throw new MoreFieldException("Слишком много аргументов");
//            }
//            return;
//        }
//        //У этих команд 1 аргумент
//        if (strcommand.equals("remove_by_id")||strcommand.equals("sort")  || strcommand.equals("execute_script")||strcommand.equals("remove_lower")) {
//            if (token.length == 2) {
//                String arg = token[1];
//                if (strcommand.equals("remove_by_id")){
//                    Chek.IDlond(arg);
//                    return;
//                }
//                if (strcommand.equals("execute_script")) {
//                    File file = new File(arg);
//                    if (file.exists() && file.isFile()) {
//                        return;
//                    } else {
//                        throw new FileNotFind("Файл с именем: " + arg + " не найден.");
//                    }
//                }
//                if (strcommand.equals("remove_lower")){
//                    Chek.price(arg);
//                    return;
//                }
//                if (strcommand.equals("remove_lower")){
//                    Chek.IDint(arg);
//                    int id  =Integer.parseInt(arg);
//                    if (id==1||id==2||id==3||id==4){
//                    return;}
//                    else{throw new MissingFieldException("Введён неверный тип сортивки");}
//                }
//
//            }
//            if (token.length > 2) {
//                throw new MoreFieldException("Слишком много аргументов");
//            } else {
//                throw new MissingFieldException("Недостаточно аргументов.");
//            }
//        }
//
//        // Далее идёт проверка для команд у которых 2 обязательных и 1 доп аргумент
//        if (strcommand.equals("add") || strcommand.equals("add_if_max")) {
//            if (token.length < 3) {
//                throw new MissingFieldException("Недостаточно аргументов.");
//            }
//            String name = token[1];
//            String priceStr = token[2];
//            // Проверка на пустое имя
//            Chek.name(name);
//            // Проверка на положительную цену
//            Chek.price(priceStr);
//            if (token.length >4){
//                throw new MoreFieldException("Слишком много аргументов");
//            }
//        }
//        // команда с 4 или 5 арг, где поля как в add
//        if (strcommand.equals("update_id")){
//            if (token.length < 4) {
//                throw new MissingFieldException("Недостаточно аргументов.");
//            }
//            //проверяем корректность id
//            Chek.IDlond(token[1]);
//            // Проверка на пустое имя
//            Chek.name(token[2]);
//            // Проверка на положительную цену
//            Chek.price(token[3]);
//            if (token.length >5){
//                throw new MoreFieldException("Слишком много аргументов");
//            }
//        }
//        //команды remove_all_by_event и remove_any_by_event у них аргументы это поля event
//        if (strcommand.equals("remove_any_by_event")){
//            if (token.length < 4) {
//                throw new MissingFieldException("Недостаточно аргументов.");
//            }
//            //проверяем корректность idEvent
//            Chek.IDint(token[1]);
//            // Проверка на пустое имя
//            Chek.name(token[2]);
//            //проверка корректность даты
//            Chek.dateEventInFile(token[3]);
//            //Проверка eventType
//            if(token.length==5){
//                Chek.EventType(token[4]);
//            }
//            if (token.length >5){
//                throw new MoreFieldException("Слишком много аргументов");
//            }
//        }
//        if (strcommand.equals("remove_all_by_event")){
//            if (token.length < 3) {
//                throw new MissingFieldException("Недостаточно аргументов.");
//            }
//
//            Chek.name(token[1]);
////
//            //проверка корректность даты
//            Chek.dateEventInFile(token[2]);
////
//            //Проверка eventType
//            if(token.length==4){
//                Chek.EventType(token[3]);
//            }
//            if (token.length >4){
//                throw new MoreFieldException("Слишком много аргументов");
//            }
//        }
//    }
//}
