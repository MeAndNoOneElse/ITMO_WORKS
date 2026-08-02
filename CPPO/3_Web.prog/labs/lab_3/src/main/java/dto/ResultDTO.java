package dto;


import java.io.Serializable;
import java.text.SimpleDateFormat;
import java.util.Date;

public class ResultDTO implements Serializable {

    private double x;
    private String y;
    private double r;
    private boolean hit;
    private Date date;
    private long time;

    public ResultDTO() {
    }

    public ResultDTO(double x, String y, double r, boolean hit, Date date, long time) {
        this.x = x;
        this.y = y;
        this.r = r;
        this.hit = hit;
        this.date = date;
        this.time = time;
    }

    public double getX() {
        return x;
    }

    public String getY() {
        return y;
    }

    public double getR() {
        return r;
    }

    public boolean isHit() {
        return hit;
    }

    public String getDate() {
        if (date == null) return "";
        SimpleDateFormat fmt = new SimpleDateFormat("HH:mm:ss, dd.MM.yyyy");
        return fmt.format(date);
    }

    public long getTime() {
        return time;
    }

    public void setDate(Date date) {
        this.date = date;
    }
    public void setTime(long time) {this.time = time;}
    public void setX(double x) {
        this.x = x;
    }
    public void setY(String y) {
        this.y = y;
    }
    public void setR(double r) {this.r = r;}
    public void setHit(boolean hit) {this.hit = hit;}

}
