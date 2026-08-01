package moves.status;

import ru.ifmo.se.pokemon.*;

public final class Swagger extends StatusMove {
    public Swagger() {
        super(Type.NORMAL, 0, 0.85);
    }

    @Override
    protected String describe() {
        return ("использует Swagger");
    }

    @Override
    protected void applyOppEffects(Pokemon p) {
        Effect.confuse(p);
        p.addEffect(new Effect().stat(Stat.ATTACK, +2));

    }
}
