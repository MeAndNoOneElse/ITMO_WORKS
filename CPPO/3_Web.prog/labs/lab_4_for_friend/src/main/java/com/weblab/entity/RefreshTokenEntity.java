package com.weblab.entity;

import jakarta.persistence.*;

/**
 * JPA-сущность refresh-токена.
 */
@Entity
@Table(name = "refresh_tokens")
public class RefreshTokenEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    private UserEntity user;

    @Column(name = "token", nullable = false, unique = true, length = 512)
    private String token;

    /** UNIX epoch millis — когда истекает */
    @Column(name = "expires_at", nullable = false)
    private Long expiresAt;

    public RefreshTokenEntity() {}

    public RefreshTokenEntity(UserEntity user, String token, Long expiresAt) {
        this.user = user;
        this.token = token;
        this.expiresAt = expiresAt;
    }

    public Long getId() { return id; }
    public UserEntity getUser() { return user; }
    public String getToken() { return token; }
    public Long getExpiresAt() { return expiresAt; }
}

