package com.weblab.dto;

/**
 * Запрос на проверку/добавление точки.
 */
public class PointRequest {
    private Double x;
    private Double y;
    private Double r;

    public Double getX() { return x; }
    public void setX(Double x) { this.x = x; }
    public Double getY() { return y; }
    public void setY(Double y) { this.y = y; }
    public Double getR() { return r; }
    public void setR(Double r) { this.r = r; }
}

