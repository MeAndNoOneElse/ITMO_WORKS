package com.weblab.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RegisterRequest {
    private String email;
    private String username;
    private String password;
    private String deviceName;
    private Integer expirationMinutes;

    public String getEmail() {
        return (email == null || email.isEmpty()) ? username : email;
    }

    public String getUsername() {
        return (username == null || username.isEmpty()) ? email : username;
    }
}