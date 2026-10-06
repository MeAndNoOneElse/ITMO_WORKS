package mypokemon;

import moves.physical.*;
import moves.status.*;
import ru.ifmo.se.pokemon.*;

public class Spinarak extends Pokemon {
    public Spinarak(String name, int lvl) {
        super(name, lvl);
        setType(Type.BUG, Type.POISON);
        setStats(40, 60, 40, 40, 40, 30);
        setMove(new Swagger(), new Fury_Swipes(), new Confide());
    }
}
