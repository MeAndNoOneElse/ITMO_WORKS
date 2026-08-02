package com.weblab.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "username", nullable = false, unique = true)
    private String username;

    @Column(name = "email", nullable = false)
    private String email;

    @Column(name = "password_hash", nullable = false)
    private String password;

    @Column(name = "auth_type")
    private String authType;

    @Transient
    private Long createdAt;

    @PrePersist
    protected void onCreate() {
        if (authType == null || authType.isEmpty()) {
            authType = "LOCAL";
        }
        if (email == null || email.isEmpty()) {
            email = username;
        }

        createdAt = System.currentTimeMillis();
    }
}