package modules;

public class Coordinates {
    private  Double x; //Поле не может быть null
    private  float y; //Значение поля должно быть больше -121
    public Coordinates(Double x, float y){
        this.x = x;
        this.y = y;
    }

    public Double getX() {
        return x;
    }

    public float getY() {
        return y;
    }

    @Override
    public String toString() {
        return "("+ x +";" + y + ")";
    }
}

