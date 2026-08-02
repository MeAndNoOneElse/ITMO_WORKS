package com.weblab.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

/**
 * Утилиты для генерации и проверки JWT-токенов.
 */
public class JwtUtil {

    private static final String SECRET = "weblab4_jaxrs_secret_key_very_long_for_security_2024";
    private static final String REFRESH_SECRET = "weblab4_jaxrs_refresh_secret_key_very_long_too_2024";

    // access: 15 минут
    private static final long ACCESS_TTL_MS = 15 * 60 * 1000L;
    // refresh: 7 дней
    private static final long REFRESH_TTL_MS = 7L * 24 * 60 * 60 * 1000L;

    private static SecretKey accessKey() {
        return Keys.hmacShaKeyFor(SECRET.getBytes(StandardCharsets.UTF_8));
    }

    private static SecretKey refreshKey() {
        return Keys.hmacShaKeyFor(REFRESH_SECRET.getBytes(StandardCharsets.UTF_8));
    }

    public static String generateAccessToken(long userId, String username) {
        return Jwts.builder()
                .subject(String.valueOf(userId))
                .claim("username", username)
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + ACCESS_TTL_MS))
                .signWith(accessKey())
                .compact();
    }

    public static String generateRefreshToken(long userId, String username) {
        return Jwts.builder()
                .subject(String.valueOf(userId))
                .claim("username", username)
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + REFRESH_TTL_MS))
                .signWith(refreshKey())
                .compact();
    }

    /**
     * Проверяет access-токен и возвращает Claims.
     * Выбрасывает исключение если токен недействителен.
     */
    public static Claims validateAccessToken(String token) {
        return Jwts.parser()
                .verifyWith(accessKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    /**
     * Проверяет refresh-токен и возвращает Claims.
     */
    public static Claims validateRefreshToken(String token) {
        return Jwts.parser()
                .verifyWith(refreshKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    public static long getUserId(Claims claims) {
        return Long.parseLong(claims.getSubject());
    }

    public static String getUsername(Claims claims) {
        return claims.get("username", String.class);
    }
}

