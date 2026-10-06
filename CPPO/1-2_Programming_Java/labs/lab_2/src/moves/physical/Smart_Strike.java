package moves.physical;

import ru.ifmo.se.pokemon.*;

public final class Smart_Strike extends PhysicalMove {
    public Smart_Strike() {
        super(Type.STEEL, 70, 0);
    }

    @Override
    protected String describe() {
        return ("использует Smart Strike");
    }
}
