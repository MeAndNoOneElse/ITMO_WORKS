package entity;


import jakarta.persistence.*;

import java.util.Date;

@Entity
@Table(name = "results")
public class ResultEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name = "user_id", nullable = false)
    double userId;
    @Column(name = "x_coord", nullable = false)
    private double x;
    @Column(name = "y_coord", nullable = false)
    private double y;
    @Column(name = "radius", nullable = false)
    private double r;
    @Column(name = "hit_result", nullable = false)
    private boolean isHit;

    @Temporal(TemporalType.TIMESTAMP)
    @Column(name = "created_at", nullable = false)
    private Date timestamp;
    @Column(name = "execution_time")
    private long executionTimeNano;

    public ResultEntity() {}
    public ResultEntity(double userId,  double x, double y, double r, boolean hit, Date timestamp,long executionTimeNano ) {
        this();
        this.userId = userId;
        this.x = x;
        this.y = y;
        this.r = r;
        this.isHit = hit;
        this.timestamp = new Date();
        this.executionTimeNano = System.nanoTime();
    }
//    @ManyToOne(fetch = FetchType.LAZY)
//    @JoinColumn(name = "user_id", nullable = false)
//    private UserEntity user;

    // геттеры и сеттеры для всех полей

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public double getX() {
        return x;
    }

    public void setX(double x) {
        this.x = x;
    }

    public double getY() {
        return y;
    }

    public void setY(double y) {
        this.y = y;
    }

    public double getR() {
        return r;
    }

    public void setR(double r) {
        this.r = r;
    }

    public boolean isHit() {
        return isHit;
    }

    public void setHit(boolean hit) {
        this.isHit = hit;
    }

    public Date getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(Date timestamp) {
        this.timestamp = timestamp;
    }

    public long getExecutionTimeNano() {
        return executionTimeNano;
    }

    public void setExecutionTimeNano(long executionTimeNano) {
        this.executionTimeNano = executionTimeNano;
    }

    public double getUserId() {
        return userId;
    }
    public void setUserId(double userId) {}
//    public UserEntity getUser() {
//        return user;
//    }
//
//    public void setUser(UserEntity user) {
//        this.user = user;
//    }
}
