package com.weblab.controller;

import com.weblab.dto.*;
import com.weblab.service.AuthService;
import com.weblab.service.SessionService;
import com.weblab.util.RequestUtils;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@Slf4j
public class AuthController {

    private final AuthService authService;

    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(
            @RequestBody RegisterRequest request,
            @RequestHeader(value = "User-Agent", required = false) String userAgent,
            @RequestHeader(value = "X-Forwarded-For", required = false) String xForwardedFor) {
        try {
            String ipAddress = RequestUtils.extractIpAddress(xForwardedFor);
            AuthResponse response = authService.register(request, ipAddress, userAgent);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(
                AuthResponse.builder()
                    .success(false)
                    .message(e.getMessage())
                    .build()
            );
        }
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(
            @RequestBody LoginRequest request,
            @RequestHeader(value = "User-Agent", required = false) String userAgent,
            @RequestHeader(value = "X-Forwarded-For", required = false) String xForwardedFor) {
        try {
            String ipAddress = RequestUtils.extractIpAddress(xForwardedFor);
            AuthResponse response = authService.login(request, ipAddress, userAgent);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(
                AuthResponse.builder()
                    .success(false)
                    .message(e.getMessage())
                    .build()
            );
        }
    }


    @PostMapping("/refresh")
    public ResponseEntity<AuthResponse> refresh(@RequestBody RefreshTokenRequest request) {
        try {
            SessionService.TokenPair tokens = authService.refreshAccessToken(request.getRefreshToken());
            return ResponseEntity.ok(
                AuthResponse.builder()
                    .success(true)
                    .message("Access token обновлен")
                    .token(tokens.getAccessToken())
                    .sessionId(tokens.getSessionId())
                    .build()
            );
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(
                AuthResponse.builder()
                    .success(false)
                    .message(e.getMessage())
                    .build()
            );
        }
    }

    @PostMapping("/logout")
    public ResponseEntity<AuthResponse> logout(HttpServletRequest request) {
        try {
            Long sessionId = RequestUtils.getSessionId(request);
            Long userId = RequestUtils.getUserId(request);

            if (sessionId != null && userId != null) {
                authService.closeSession(sessionId, userId);
                log.info("User {} logged out, session {} closed", userId, sessionId);
            }

            return ResponseEntity.ok(
                AuthResponse.builder()
                    .success(true)
                    .message("Выход выполнен")
                    .build()
            );
        } catch (Exception e) {
            log.error("Logout error: {}", e.getMessage());
            return ResponseEntity.ok(
                AuthResponse.builder()
                    .success(true)
                    .message("Выход выполнен")
                    .build()
            );
        }
    }

    @GetMapping("/check-session")
    public ResponseEntity<Void> checkSession() {
        return ResponseEntity.ok().build();
    }
}

