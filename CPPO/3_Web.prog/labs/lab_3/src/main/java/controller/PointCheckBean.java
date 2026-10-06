package controller;

import dto.PointDTO;
import dto.ResultDTO;

import jakarta.inject.Inject;
import jakarta.faces.view.ViewScoped;
import jakarta.inject.Named;

import java.io.Serializable;

import service.CachingAreaCheckService;

@Named
@ViewScoped
public class PointCheckBean implements Serializable {

    @Inject
    private CachingAreaCheckService cacheService;

    @Inject
    private ResultsBean resultsBean;

    private double x;
    private String y = "0";
    private double r = 2.0;

    // Getters and Setters
    public double getX() {
        return x;
    }

    public void setX(double x) {
        this.x = x;
    }

    public String getY() {
        return y;
    }

    public void setY(String y) {
        this.y = y;
    }

    public Double getR() {
        return r;
    }

    public void setR(Double r) {
        if (r != null) {
            this.r = r; // сохраняем новый выбор
        }
    }

    public String checkArea() {
        PointDTO pointDTO = new PointDTO(x, y, r);
        ResultDTO result = cacheService.checkAndSave(pointDTO);
        resultsBean.addResult(result);
        return null;
    }
}
