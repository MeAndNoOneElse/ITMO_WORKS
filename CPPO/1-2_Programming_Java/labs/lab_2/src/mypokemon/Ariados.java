package mypokemon;

import moves.physical.*;
import moves.status.*;
import ru.ifmo.se.pokemon.*;

public final class Ariados extends Spinarak {
    public Ariados(String name, int lvl) {
        super(name, lvl);
        setType(Type.BUG, Type.POISON);
        setStats(70, 90, 70, 60, 70, 40);
        setMove(new Swagger(), new Fury_Swipes(), new Confide(), new Smart_Strike());
    }
}
