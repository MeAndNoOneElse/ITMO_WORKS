package moves.status;

import ru.ifmo.se.pokemon.*;

public final class Double_Team extends StatusMove {
    public Double_Team() {
        super(Type.NORMAL, 0, 0);
    }

    @Override
    protected String describe() {
        return ("исполльзует  Double Team");
    }

    @Override
    protected void applySelfEffects(Pokemon p) {
        p.addEffect(new Effect().stat(Stat.DEFENSE, +1));
    }
}
