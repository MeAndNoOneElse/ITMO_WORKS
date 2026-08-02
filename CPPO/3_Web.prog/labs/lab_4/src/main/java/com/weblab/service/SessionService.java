package com.weblab.service;

import com.weblab.entity.Session;
import com.weblab.entity.User;
import com.weblab.repository.SessionRepository;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class SessionService {

    private final SessionRepository sessionRepository;
    private final JwtTokenProvider jwtTokenProvider;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    @Transactional
    public TokenPair createSession(User user, String deviceName, String ipAddress, String userAgent) {
        LocalDateTime now = LocalDateTime.now();

        Session session = new Session();
        session.setUser(user);
        session.setDeviceName(deviceName != null ? deviceName : "Unknown Device");
        session.setIpAddress(ipAddress);
        session.setUserAgent(userAgent);
        session.setStatus("OPEN");
        session.setCreatedAt(now);
        session.setLastActivity(now);
        session.setAccessExpiresAt(now.plusDays(1));
        session.setRefreshExpiresAt(now.plusMinutes(1));

        Session savedSession = sessionRepository.save(session);

        String accessToken = jwtTokenProvider.generateToken(
            user.getId(),
            user.getUsername(),
            user.getEmail(),
            savedSession.getId(),
            24 * 60
        );

        String refreshToken = jwtTokenProvider.generateRefreshToken(
            savedSession.getId(),
            user.getId(),
            1
        );

        savedSession.setRefreshTokenHash(passwordEncoder.encode(refreshToken));
        sessionRepository.save(savedSession);

        log.info("Session created: userId={}, sessionId={}, device={}, access=1d, refresh=1min",
            user.getId(), savedSession.getId(), deviceName);

        return new TokenPair(accessToken, refreshToken, savedSession.getId());
    }

    @Transactional
    public TokenPair refreshAccessToken(String refreshToken) {
        if (!jwtTokenProvider.validateToken(refreshToken)) {
            log.warn("Invalid refresh token JWT");
            throw new IllegalArgumentException("Invalid refresh token");
        }

        Long sessionId = jwtTokenProvider.getSessionIdFromToken(refreshToken);
        Long userId = jwtTokenProvider.getUserIdFromToken(refreshToken);

        if (sessionId == null || userId == null) {
            throw new IllegalArgumentException("Invalid refresh token structure");
        }

        Optional<Session> sessionOpt = sessionRepository.findById(sessionId);
        if (sessionOpt.isEmpty()) {
            log.warn("Session {} not found", sessionId);
            throw new IllegalArgumentException("Session not found");
        }

        Session session = sessionOpt.get();

        if (!"OPEN".equals(session.getStatus())) {
            log.warn("Session {} is CLOSED", sessionId);
            throw new IllegalArgumentException("Session is closed");
        }

        if (!session.isRefreshValid()) {
            log.warn("Refresh token expired for session {}", sessionId);
            throw new IllegalArgumentException("Refresh token expired");
        }

        if (!session.getUser().getId().equals(userId)) {
            throw new IllegalArgumentException("Invalid session");
        }

        if (session.getRefreshTokenHash() == null ||
            !passwordEncoder.matches(refreshToken, session.getRefreshTokenHash())) {
            log.warn("Refresh token hash mismatch for session {}", sessionId);
            throw new IllegalArgumentException("Invalid refresh token");
        }

        LocalDateTime now = LocalDateTime.now();
        User user = session.getUser();

        String newAccessToken = jwtTokenProvider.generateToken(
            user.getId(),
            user.getUsername(),
            user.getEmail(),
            sessionId,
            24 * 60
        );

        session.setLastActivity(now);
        session.setAccessExpiresAt(now.plusDays(1));
        sessionRepository.save(session);

        log.info("Access token refreshed for session {}", sessionId);

        return new TokenPair(newAccessToken, null, sessionId);
    }

    public List<Session> getOpenSessionsByUser(User user) {
        return sessionRepository.findOpenSessionsByUser(user);
    }

    public List<Session> getOtherOpenSessions(User user, Long currentSessionId) {
        return sessionRepository.findOpenSessionsByUserExceptCurrent(user, currentSessionId);
    }

    public Optional<Session> findById(Long sessionId) {
        return sessionRepository.findById(sessionId);
    }

    @Transactional
    public void closeSession(Long sessionId, Long userId) {
        int updated = sessionRepository.closeSessionByIdAndUserId(sessionId, userId);
        if (updated > 0) {
            log.info("Session {} closed", sessionId);
        } else {
            log.warn("Session {} not found or already closed", sessionId);
        }
    }

    @Transactional
    public int closeOtherSessions(Long userId, Long currentSessionId) {
        int closed = sessionRepository.closeOtherSessions(userId, currentSessionId);
        log.info("Closed {} other sessions for user {}", closed, userId);
        return closed;
    }

    @Data
    public static class TokenPair {
        private final String accessToken;
        private final String refreshToken;
        private final Long sessionId;
    }
}


