package moves.physical;

import ru.ifmo.se.pokemon.*;

public final class Fury_Swipes extends PhysicalMove {
    public Fury_Swipes() {
        super(Type.NORMAL, 18, 0.8);
    }

    @Override
    protected String describe() {
        return ("использует Fury Swipes");
    }
}
