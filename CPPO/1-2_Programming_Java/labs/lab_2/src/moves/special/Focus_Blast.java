package moves.special;

import ru.ifmo.se.pokemon.*;

public final class Focus_Blast extends SpecialMove {
    public Focus_Blast() {
        super(Type.FIGHTING, 120, 0.7);
    }

    @Override
    protected String describe() {
        return ("использует Focus Blast");
    }

    @Override
    protected void applyOppEffects(Pokemon p) {
        if (Math.random() <= 0.1) {
            p.addEffect(new Effect().stat(Stat.SPECIAL_DEFENSE, -1));
        }
    }
}
