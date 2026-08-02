package com.weblab.dto;

/**
 * Запрос на обновление access-токена.
 */
public class RefreshTokenRequest {
    private String refreshToken;

    public String getRefreshToken() { return refreshToken; }
    public void setRefreshToken(String refreshToken) { this.refreshToken = refreshToken; }
}

