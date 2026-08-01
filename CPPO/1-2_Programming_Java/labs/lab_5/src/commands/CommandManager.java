package commands;

import java.util.HashMap;

/**
 * @author Andrey Anufriev
 * класс для создания экземпляров команд
 */
public class CommandManager {
    public static HashMap<String, Command> CommandMap = new HashMap<>();

    /**
     *
     * создаёт обЪекты команд и добавляет их в HashMap
     */
    public static void AddCommand(){
        CommandMap.put("help", new HelpCommand());
        CommandMap.put("exit", new ExitCommand());
        CommandMap.put("add", new AddCommand());
        CommandMap.put("info", new InfoCommand());
        CommandMap.put("show", new ShowCommand());
        CommandMap.put("add_if_max", new AddIfMaxCommand());
        CommandMap.put("update_id", new UpdateCommand());
        CommandMap.put("remove_by_id", new RemoveById());
        CommandMap.put("clear", new ClearCommand());
        CommandMap.put("save", new SaveCommand());
        CommandMap.put("print_unique_price", new PrintUniquePrice());
        CommandMap.put("execute_script", new ExecuteScript());
        CommandMap.put("remove_first", new RemoveFirst());
        CommandMap.put("remove_lower", new RemoveLower());
        CommandMap.put("remove_all_by_event", new RemoveAllByEvent());
        CommandMap.put("remove_any_by_event", new RemoveAnyByEvent());
        CommandMap.put("sort", new Sort());
    }
}
