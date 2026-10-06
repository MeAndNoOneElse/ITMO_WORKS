package moves.status;

import ru.ifmo.se.pokemon.*;

public final class Swords_Dance extends StatusMove {
    public Swords_Dance() {
        super(Type.NORMAL, 0, 0);
    }

    @Override
    protected void applySelfEffects(Pokemon p) {
        p.addEffect(new Effect().stat(Stat.ATTACK, (int) p.getStat(Stat.ATTACK) + 2));
    }

    @Override
    protected String describe() {
        return "использует  Swords Dance";
    }
}
