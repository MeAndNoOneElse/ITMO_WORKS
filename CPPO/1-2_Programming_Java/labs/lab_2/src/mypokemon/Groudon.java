package mypokemon;

import moves.physical.*;
import moves.special.*;
import moves.status.*;
import ru.ifmo.se.pokemon.*;

public final class Groudon extends Pokemon {
    public Groudon(String name, int lvl) {
        super(name, lvl);
        setType(Type.GROUND);
        setStats(100, 150, 140, 100, 90, 90);
        setMove(new Aerial_Ace(), new Swords_Dance(), new Focus_Blast(), new Double_Team());
    }
}

