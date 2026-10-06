package com.weblab.entity;

import jakarta.persistence.*;
import java.time.Instant;

/**
 * JPA-сущность точки (результата).
 * createdAt хранится как UNIX-timestamp в миллисекундах (UTC).
 * Фронт получает epochMilli и сам форматирует через new Date(epochMilli).
 */
@Entity
@Table(name = "points")
public class PointEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    private UserEntity user;

    @Column(name = "x", nullable = false)
    private Double x;

    @Column(name = "y", nullable = false)
    private Double y;

    @Column(name = "r", nullable = false)
    private Double r;

    @Column(name = "hit", nullable = false)
    private Boolean hit;

    /** Время выполнения в микросекундах */
    @Column(name = "execution_time", nullable = false)
    private Long executionTime;

    /**
     * Абсолютное время создания точки — UNIX epoch millis (UTC).
     * Хранится как BIGINT, не зависит от часового пояса сервера.
     */
    @Column(name = "created_at_epoch", nullable = false)
    private Long createdAtEpoch;

    public PointEntity() {}

    public PointEntity(UserEntity user, Double x, Double y, Double r,
                       Boolean hit, Long executionTime) {
        this.user = user;
        this.x = x;
        this.y = y;
        this.r = r;
        this.hit = hit;
        this.executionTime = executionTime;
        this.createdAtEpoch = Instant.now().toEpochMilli();
    }

    public Long getId() { return id; }
    public UserEntity getUser() { return user; }
    public Double getX() { return x; }
    public Double getY() { return y; }
    public Double getR() { return r; }
    public Boolean getHit() { return hit; }
    public Long getExecutionTime() { return executionTime; }
    public Long getCreatedAtEpoch() { return createdAtEpoch; }
    public void setCreatedAtEpoch(Long createdAtEpoch) { this.createdAtEpoch = createdAtEpoch; }
}

