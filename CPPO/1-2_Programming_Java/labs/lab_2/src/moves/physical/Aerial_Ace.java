package moves.physical;

import ru.ifmo.se.pokemon.*;

public final class Aerial_Ace extends PhysicalMove {
    public Aerial_Ace() {
        super(Type.FLYING, 60, 1);
    }

    @Override
    public String describe() {
        return "использует Aerial Ace";
    }
}

