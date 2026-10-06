package com.weblab.dto;

/**
 * Запрос на вход.
 */
public class LoginRequest {
    private String username;
    private String email;
    private String password;
    private String deviceName;

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) { this.username = username; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
    public String getDeviceName() { return deviceName; }
    public void setDeviceName(String deviceName) { this.deviceName = deviceName; }
}

