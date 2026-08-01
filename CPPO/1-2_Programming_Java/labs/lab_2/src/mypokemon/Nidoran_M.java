package mypokemon;

import moves.physical.*;
import moves.special.*;
import ru.ifmo.se.pokemon.*;

public class Nidoran_M extends Pokemon {
    public Nidoran_M(String name, int lvl) {
        super(name, lvl);
        setType(Type.POISON);
        setStats(46, 57, 40, 40, 40, 50);
        setMove(new Thunder(), new Poison_Sting());
    }
}
