
import mypokemon.*;
import ru.ifmo.se.pokemon.*;

public class Main {
    public static void main(String[] args) {
        Battle a = new Battle();

        a.addFoe(new Ariados("Ivan", 30));
        a.addFoe(new Groudon("Vasiliy", 30));
        a.addFoe(new Nidoking("Petr", 30));
        a.addAlly(new Nidorino("Ibragim", 30));
        a.addAlly(new Nidoran_M("Muxamed", 30));
        a.addAlly(new Spinarak("Abdulla", 30));
        a.go();
    }
}