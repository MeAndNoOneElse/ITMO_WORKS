package com.weblab.service;

import com.weblab.dto.*;
import com.weblab.entity.Session;
import com.weblab.entity.User;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class AuthService {

    private final UserService userService;
    private final SessionService sessionService;

    @Transactional
    public AuthResponse register(RegisterRequest request, String ipAddress, String userAgent) {
        validateCredentials(request.getUsername(), request.getPassword());

        User user = userService.register(request);

        SessionService.TokenPair tokens = sessionService.createSession(
            user,
            request.getDeviceName() != null ? request.getDeviceName() : "Web Browser",
            ipAddress,
            userAgent
        );

        log.info("User registered: {}, sessionId={}", user.getUsername(), tokens.getSessionId());

        return AuthResponse.builder()
            .success(true)
            .message("Регистрация успешна")
            .user(AuthResponse.UserDTO.fromUser(user))
            .token(tokens.getAccessToken())
            .refreshToken(tokens.getRefreshToken())
            .sessionId(tokens.getSessionId())
            .build();
    }

    @Transactional
    public AuthResponse login(LoginRequest request, String ipAddress, String userAgent) {
        validateCredentials(request.getUsername(), request.getPassword());

        User user = authenticateUser(request.getUsername(), request.getPassword());

        SessionService.TokenPair tokens = sessionService.createSession(
            user,
            request.getDeviceName() != null ? request.getDeviceName() : "Web Browser",
            ipAddress,
            userAgent
        );

        List<Session> otherActiveSessions = sessionService.getOpenSessionsByUser(user).stream()
            .filter(s -> !s.getId().equals(tokens.getSessionId()))
            .toList();

        log.info("User logged in: {}, sessionId={}, other active sessions={}",
            user.getUsername(), tokens.getSessionId(), otherActiveSessions.size());

        return AuthResponse.builder()
            .success(true)
            .message(otherActiveSessions.isEmpty() ? "Вход выполнен" : "Вход выполнен. У вас есть другие активные сессии.")
            .user(AuthResponse.UserDTO.fromUser(user))
            .token(tokens.getAccessToken())
            .refreshToken(tokens.getRefreshToken())
            .sessionId(tokens.getSessionId())
            .hasActiveSessions(!otherActiveSessions.isEmpty())
            .activeSessions(SessionClosedDTO.fromSessions(otherActiveSessions))
            .build();
    }

    @Transactional
    public SessionService.TokenPair refreshAccessToken(String refreshToken) {
        return sessionService.refreshAccessToken(refreshToken);
    }
    @Transactional(readOnly = true)
    public List<SessionClosedDTO> getUserSessions(Long userId, Long currentSessionId) {
        User user = userService.findById(userId)
            .orElseThrow(() -> new IllegalArgumentException("User not found"));

        List<Session> sessions = sessionService.getOtherOpenSessions(user, currentSessionId);
        return SessionClosedDTO.fromSessions(sessions);
    }

    @Transactional
    public void closeSession(Long sessionId, Long userId) {
        sessionService.closeSession(sessionId, userId);
    }

    @Transactional
    public int closeOtherSessions(Long userId, Long currentSessionId) {
        return sessionService.closeOtherSessions(userId, currentSessionId);
    }


    private void validateCredentials(String username, String password) {
        if (username == null || username.trim().isEmpty()) {
            throw new IllegalArgumentException("Username не может быть пустым");
        }
        if (password == null || password.isEmpty()) {
            throw new IllegalArgumentException("Пароль не может быть пустым");
        }
    }

    private User authenticateUser(String username, String password) {
        User user = userService.findByUsername(username)
            .orElseThrow(() -> new IllegalArgumentException("Неверный username или пароль"));

        if (!userService.checkPassword(password, user.getPassword())) {
            throw new IllegalArgumentException("Неверный username или пароль");
        }

        return user;
    }
}

