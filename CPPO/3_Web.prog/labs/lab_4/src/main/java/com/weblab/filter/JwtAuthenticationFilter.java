package com.weblab.filter;

import com.weblab.entity.Session;
import com.weblab.service.JwtTokenProvider;
import com.weblab.service.SessionService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.annotation.Order;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Optional;

@Component
@Order(1)
@RequiredArgsConstructor
@Slf4j
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtTokenProvider jwtTokenProvider;
    private final SessionService sessionService;

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain filterChain
    ) throws ServletException, IOException {

        String path = request.getRequestURI();
        if (isPublicEndpoint(path)) {
            filterChain.doFilter(request, response);
            return;
        }

        String token = extractToken(request);

        if (token == null || token.isEmpty()) {
            log.debug("Request without token to protected endpoint: {}", path);
            jwtTokenProvider.sendUnauthorizedError(response, "Token not provided");
            return;
        }

        if (!jwtTokenProvider.validateToken(token)) {
            log.debug("Invalid JWT token for endpoint: {}", path);
            jwtTokenProvider.sendUnauthorizedError(response, "Invalid or expired token");
            return;
        }

        Long userId = jwtTokenProvider.getUserIdFromToken(token);
        String username = jwtTokenProvider.getUsernameFromToken(token);
        Long sessionId = jwtTokenProvider.getSessionIdFromToken(token);

        if (userId == null) {
            log.debug("Cannot extract userId from token for endpoint: {}", path);
            jwtTokenProvider.sendUnauthorizedError(response, "Invalid token structure");
            return;
        }

        if (sessionId != null) {
            Optional<Session> sessionOpt = sessionService.findById(sessionId);

            if (sessionOpt.isEmpty()) {
                log.warn("Session {} not found in database for user {}", sessionId, username);
                jwtTokenProvider.sendUnauthorizedError(response, "Session not found");
                return;
            }

            Session session = sessionOpt.get();

            if (!"OPEN".equals(session.getStatus())) {
                log.warn("Session {} is CLOSED (status: {}) for user {}", sessionId, session.getStatus(), username);
                jwtTokenProvider.sendUnauthorizedError(response, "Session closed");
                return;
            }

            log.debug("Session {} verified: OPEN", sessionId);
        }

        request.setAttribute("userId", userId);
        request.setAttribute("username", username);
        request.setAttribute("sessionId", sessionId);
        request.setAttribute("token", token);

        log.debug("Token is valid for user: {} (id: {}, sessionId: {}, endpoint: {})", username, userId, sessionId, path);

        filterChain.doFilter(request, response);
    }

    private String extractToken(HttpServletRequest request) {
        String authHeader = request.getHeader("Authorization");

        if (authHeader == null || authHeader.isEmpty()) {
            return null;
        }

        if (authHeader.startsWith("Bearer ")) {
            return authHeader.substring(7);
        }

        return authHeader;
    }

    private boolean isPublicEndpoint(String path) {
        return path.equals("/api/auth/login") ||
               path.equals("/api/auth/register") ||
               path.equals("/api/auth/refresh") ||
               path.startsWith("/h2-console") ||
               path.startsWith("/error");
    }
}

