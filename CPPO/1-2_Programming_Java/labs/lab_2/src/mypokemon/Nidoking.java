package mypokemon;

import moves.physical.*;
import moves.special.*;
import moves.status.*;
import ru.ifmo.se.pokemon.*;

public final class Nidoking extends Nidorino {
    public Nidoking(String name, int lvl) {
        super(name, lvl);
        setType(Type.POISON, Type.GROUND);
        setStats(81, 102, 77, 85, 75, 85);
        setMove(new Thunder(), new Poison_Sting(), new Leer(), new Shadow_Claw());
    }
}
