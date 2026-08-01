package Character;

import enums.Actions;
import enums.Type;

public class OldWomen extends Characters {
    private final String name;
    private final Type type;

    public OldWomen(String name, Type type) {
        this.name = name;
        this.type = type;
    }

    @Override
    public void say() {

    }

    @Override
    public void action() {
    }

    @Override
    public String getName(Integer x) {
        return switch (x) {
            case 1 -> "она";
            case 2 -> "ей";
            case 3 -> "её";
            case 4 -> "неё";
            default -> name;
        };
    }

    public Type getType() {
        return type;
    }

    public String removes(Object var1) {
        return getType() + " снимает с " + var1 + " платье";
    }

    public String dress() {
        return Actions.DRESSES + " в бельчью шкуру";
    }

    public String thought(Object var1, Object var2) {
        return (type + " " + Actions.THOUGHT + " " + var1 + " питательными " + var2);
    }

    public String hasNot(Object var1) {
        return (getName(1) + " не имела " + var1);
    }

    public String couldNot(Object var) {
        return ("не могла " + var + " ничего твердого");
    }

    public String drink(Object var, Object var2) {
        return (var + " " + var2 + " только такую воду");
    }

    public String took(Object var1, Object var2, Object var3) {
        return getName(1) + " " + var1 + " кокосовые " + var2 + " и, взяв в руку " + var3;
    }

    public String leave(Object var1) {
        return var1 + " уходить";
    }

    public String order(Object var1) {
        return getName(1) + "приказала " + var1 + "у, чтобы к " + getName(2) + " возвращению";
    }

    public String brought(Object var) {
        return "куда привела его " + type + " , находилась в очень отдаленной части " + var;
    }

    public String tiered() {
        return "старуха умерла";
    }

    public String cameBack(Object var) {
        return "когда " + type + " вернулась " + var + "ой она попробовала суп и ей сразу стало плохо";
    }
}
