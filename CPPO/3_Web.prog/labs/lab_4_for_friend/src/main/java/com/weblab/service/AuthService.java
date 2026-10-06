package com.weblab.service;

import com.weblab.dto.AuthResponse;
import com.weblab.dto.LoginRequest;
import com.weblab.dto.RegisterRequest;
import com.weblab.entity.UserEntity;
import com.weblab.repository.RefreshTokenRepository;
import com.weblab.repository.UserRepository;
import com.weblab.util.JwtUtil;
import org.mindrot.jbcrypt.BCrypt;

import java.util.Optional;

/**
 * Сервис аутентификации.
 */
public class AuthService {

    private final UserRepository userRepo = new UserRepository();
    private final RefreshTokenRepository tokenRepo = new RefreshTokenRepository();

    // 7 дней в мс
    private static final long REFRESH_TTL_MS = 7L * 24 * 60 * 60 * 1000L;

    public AuthResponse register(RegisterRequest req) {
        String username = req.getUsername();
        if (username == null || username.isBlank())
            throw new IllegalArgumentException("Логин обязателен");
        if (req.getPassword() == null || req.getPassword().length() < 6)
            throw new IllegalArgumentException("Пароль должен содержать минимум 6 символов");
        if (userRepo.existsByUsername(username))
            throw new IllegalArgumentException("Пользователь с таким логином уже существует");

        String hash = BCrypt.hashpw(req.getPassword(), BCrypt.gensalt());
        UserEntity user = userRepo.create(username, req.getEmail(), hash);

        String accessToken  = JwtUtil.generateAccessToken(user.getId(), username);
        String refreshToken = JwtUtil.generateRefreshToken(user.getId(), username);
        tokenRepo.save(user, refreshToken, System.currentTimeMillis() + REFRESH_TTL_MS);

        System.out.println("[AUTH] Регистрация: " + username + " (id=" + user.getId() + ")");
        return AuthResponse.builder()
                .success(true).message("Регистрация успешна")
                .token(accessToken).refreshToken(refreshToken)
                .user(new AuthResponse.UserDTO(user.getId(), username, user.getEmail()))
                .build();
    }

    public AuthResponse login(LoginRequest req) {
        String username = req.getUsername();
        if (username == null || username.isBlank() || req.getPassword() == null)
            throw new IllegalArgumentException("Логин и пароль обязательны");

        System.out.println("[AUTH] Логин: " + username);
        Optional<UserEntity> opt = userRepo.findByUsername(username);
        if (opt.isEmpty()) {
            System.out.println("[AUTH] Пользователь не найден: " + username);
            throw new IllegalArgumentException("Неверный логин или пароль");
        }

        UserEntity user = opt.get();
        if (!BCrypt.checkpw(req.getPassword(), user.getPasswordHash())) {
            System.out.println("[AUTH] Неверный пароль для: " + username);
            throw new IllegalArgumentException("Неверный логин или пароль");
        }

        String accessToken  = JwtUtil.generateAccessToken(user.getId(), username);
        String refreshToken = JwtUtil.generateRefreshToken(user.getId(), username);
        tokenRepo.save(user, refreshToken, System.currentTimeMillis() + REFRESH_TTL_MS);

        System.out.println("[AUTH] Успешный вход: " + username + " (id=" + user.getId() + ")");
        return AuthResponse.builder()
                .success(true).message("Успешный вход")
                .token(accessToken).refreshToken(refreshToken)
                .user(new AuthResponse.UserDTO(user.getId(), username, user.getEmail()))
                .build();
    }

    public AuthResponse refresh(String refreshToken) {
        if (refreshToken == null || refreshToken.isBlank())
            throw new IllegalArgumentException("Refresh токен отсутствует");

        io.jsonwebtoken.Claims claims;
        try {
            claims = JwtUtil.validateRefreshToken(refreshToken);
        } catch (Exception e) {
            throw new IllegalArgumentException("Refresh токен недействителен или истёк");
        }

        long userId   = JwtUtil.getUserId(claims);
        String username = JwtUtil.getUsername(claims);

        Optional<Long> storedUserId = tokenRepo.findUserIdByToken(refreshToken);
        if (storedUserId.isEmpty())
            throw new IllegalArgumentException("Refresh токен отозван или не найден");

        UserEntity user = userRepo.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("Пользователь не найден"));

        String newAccess  = JwtUtil.generateAccessToken(userId, username);
        String newRefresh = JwtUtil.generateRefreshToken(userId, username);
        tokenRepo.save(user, newRefresh, System.currentTimeMillis() + REFRESH_TTL_MS);

        return AuthResponse.builder()
                .success(true).message("Access токен обновлён")
                .token(newAccess).refreshToken(newRefresh)
                .build();
    }

    public void logout(long userId) {
        tokenRepo.deleteByUserId(userId);
    }
}
