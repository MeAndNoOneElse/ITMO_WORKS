package Character;

import java.util.Objects;

public abstract class Characters implements People {
    private String name;

    public abstract void say();

    public String getName(Integer x) {
        return switch (x) {
            case 1 -> "он";
            case 2 -> "ему";
            case 3 -> "его";
            case 4 -> "него";
            default -> name;
        };
    }

    public void setName(String name) {
        this.name = name;
    }

    @Override
    public String toString() {
        return this.getName(0);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Characters name = (Characters) o;
        return Objects.equals(name, this.name);
    }

    @Override
    public int hashCode() {
        return this.name.hashCode();
    }
}