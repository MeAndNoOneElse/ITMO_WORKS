package com.weblab.dto;

/**
 * Ответ с данными точки.
 * createdAt — UNIX epoch millis (UTC). Фронт использует new Date(createdAt).
 */
public class ResultResponse {
    private Long id;
    private Double x;
    private Double y;
    private Double r;
    private Boolean hit;
    /** UNIX epoch millis */
    private Long createdAt;
    private Long executionTime;

    public ResultResponse() {}

    public ResultResponse(Long id, Double x, Double y, Double r,
                          Boolean hit, Long createdAt, Long executionTime) {
        this.id = id;
        this.x = x;
        this.y = y;
        this.r = r;
        this.hit = hit;
        this.createdAt = createdAt;
        this.executionTime = executionTime;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Double getX() { return x; }
    public void setX(Double x) { this.x = x; }
    public Double getY() { return y; }
    public void setY(Double y) { this.y = y; }
    public Double getR() { return r; }
    public void setR(Double r) { this.r = r; }
    public Boolean getHit() { return hit; }
    public void setHit(Boolean hit) { this.hit = hit; }
    public Long getCreatedAt() { return createdAt; }
    public void setCreatedAt(Long createdAt) { this.createdAt = createdAt; }
    public Long getExecutionTime() { return executionTime; }
    public void setExecutionTime(Long executionTime) { this.executionTime = executionTime; }
}

