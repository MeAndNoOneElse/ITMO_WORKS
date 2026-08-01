package mypokemon;

import moves.physical.*;
import moves.special.*;
import moves.status.*;
import ru.ifmo.se.pokemon.*;

public class Nidorino extends Nidoran_M {
    public Nidorino(String name, int lvl) {
        super(name, lvl);
        setType(Type.POISON);
        setStats(61, 72, 57, 55, 55, 65);
        setMove(new Thunder(), new Poison_Sting(), new Leer());
    }
}
