package com.weblab.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.weblab.dto.AuthResponse;
import com.weblab.entity.User;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Date;

@Service
@Slf4j
public class JwtTokenProvider {

    private static final ObjectMapper objectMapper = new ObjectMapper();

    @Value("${jwt.secret:my-super-secret-key-that-is-at-least-256-bits-long-for-security-purposes}")
    private String jwtSecret;

    public String generateToken(Long userId, String username, String email, Long sessionId, int expirationMinutes) {
        try {
            SecretKey key = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));

            Instant now = Instant.now();
            Instant expiration = now.plusSeconds((long) expirationMinutes * 60);

            String token = Jwts.builder()
                    .subject(username)
                    .claim("userId", userId)
                    .claim("username", username)
                    .claim("email", email)
                    .claim("sessionId", sessionId)
                    .claim("type", "access")
                    .issuedAt(Date.from(now))
                    .expiration(Date.from(expiration))
                    .signWith(key)
                    .compact();

            log.info("JWT access token created for user: {} (sessionId: {}, expires in {} minutes)", username, sessionId, expirationMinutes);
            return token;

        } catch (Exception e) {
            log.error("Error creating JWT token: {}", e.getMessage());
            throw new RuntimeException("Failed to create JWT token", e);
        }
    }

    public String generateRefreshToken(Long sessionId, Long userId, int expirationMinutes) {
        try {
            SecretKey key = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));

            Instant now = Instant.now();
            Instant expiration = now.plusSeconds((long) expirationMinutes * 60);

            String token = Jwts.builder()
                    .subject(String.valueOf(sessionId))
                    .claim("sessionId", sessionId)
                    .claim("userId", userId)
                    .claim("type", "refresh")
                    .issuedAt(Date.from(now))
                    .expiration(Date.from(expiration))
                    .signWith(key)
                    .compact();

            log.info("Refresh token created for sessionId: {} (expires in {} minutes)", sessionId, expirationMinutes);
            return token;

        } catch (Exception e) {
            log.error("Error creating refresh token: {}", e.getMessage());
            throw new RuntimeException("Failed to create refresh token", e);
        }
    }

    public Long getUserIdFromToken(String token) {
        try {
            Claims claims = parseToken(token);
            Object userIdObj = claims.get("userId");

            if (userIdObj instanceof Integer) {
                return ((Integer) userIdObj).longValue();
            } else if (userIdObj instanceof Long) {
                return (Long) userIdObj;
            }

            return null;
        } catch (Exception e) {
            log.debug("Error getting userId from token: {}", e.getMessage());
            return null;
        }
    }

    public Long getSessionIdFromToken(String token) {
        try {
            Claims claims = parseToken(token);
            Object sessionIdObj = claims.get("sessionId");

            if (sessionIdObj instanceof Integer) {
                return ((Integer) sessionIdObj).longValue();
            } else if (sessionIdObj instanceof Long) {
                return (Long) sessionIdObj;
            }

            return null;
        } catch (Exception e) {
            log.debug("Error getting sessionId from token: {}", e.getMessage());
            return null;
        }
    }

    public String getUsernameFromToken(String token) {
        try {
            Claims claims = parseToken(token);
            return claims.get("username", String.class);
        } catch (Exception e) {
            log.debug("Error getting userName from token: {}", e.getMessage());
            return null;
        }
    }

    public String getEmailFromToken(String token) {
        try {
            Claims claims = parseToken(token);
            return claims.get("email", String.class);
        } catch (Exception e) {
            log.debug("Ошибка при получении email из токена: {}", e.getMessage());
            return null;
        }
    }

    public boolean isTokenValid(String token) {
        try {
            parseToken(token);
            return true;
        } catch (Exception e) {
            log.debug("Token is invalid: {}", e.getMessage());
            return false;
        }
    }

    public boolean validateToken(String token) {
        return isTokenValid(token);
    }

    private Claims parseToken(String token) {
        try {
            SecretKey key = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));

            return Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();
        } catch (Exception e) {
            log.debug("Error parsing token: {} - {}", e.getClass().getSimpleName(), e.getMessage());
            throw e;
        }
    }

    public void sendJsonResponse(HttpServletResponse response, int status, Object body) throws IOException {
        response.setStatus(status);
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");
        response.getWriter().write(objectMapper.writeValueAsString(body));
    }

    public void sendUnauthorizedError(HttpServletResponse response, String message) throws IOException {
        AuthResponse errorResponse = new AuthResponse(false, message, null, null);
        sendJsonResponse(response, HttpServletResponse.SC_UNAUTHORIZED, errorResponse);
    }
}

