package dto;

import java.io.Serializable;

public class PointDTO  implements Serializable {
    private double x;
    private String y;
    private double r;

    public PointDTO() {}

    public PointDTO(double x, String y, double r){
        this.x = x;
        this.y = y;
        this.r = r;
    }

    public double getX() { return x; }
    public void setX(double x) { this.x = x; }

    public String getY() { return y; }
    public void setY(String y) { this.y = y; }

    public double getR() { return r; }
    public void setR(double r) { this.r = r; }
}
