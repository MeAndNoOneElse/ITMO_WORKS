package moves.physical;

import ru.ifmo.se.pokemon.*;

public final class Poison_Sting extends PhysicalMove {
    public Poison_Sting() {
        super(Type.POISON, 15, 1);
    }

    @Override
    protected String describe() {
        return ("использует Poison Sting");
    }

    @Override
    protected void applyOppEffects(Pokemon p) {
        if (Math.random() <= 0.3) {
            Effect.poison(p);
        }
    }
}
