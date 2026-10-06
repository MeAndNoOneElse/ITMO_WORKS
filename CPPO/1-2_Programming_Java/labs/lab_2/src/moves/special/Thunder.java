package moves.special;

import ru.ifmo.se.pokemon.*;

public final class Thunder extends SpecialMove {
    public Thunder() {
        super(Type.ELECTRIC, 110, 0.7);
    }

    @Override
    protected String describe() {
        return ("использует Thunder");
    }

    @Override
    protected void applyOppEffects(Pokemon p) {
        if (Math.random() <= 0.3) {
            Effect.paralyze(p);
        }
    }
}
