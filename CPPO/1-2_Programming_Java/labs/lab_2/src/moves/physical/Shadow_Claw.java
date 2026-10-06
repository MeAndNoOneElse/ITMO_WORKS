package moves.physical;

import ru.ifmo.se.pokemon.PhysicalMove;
import ru.ifmo.se.pokemon.Type;

public final class Shadow_Claw extends PhysicalMove {
    public Shadow_Claw() {
        super(Type.GHOST, 70, 1);
    }

    @Override
    protected String describe() {
        return ("использует Shadow Claw");
    }
}
