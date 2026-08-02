package com.weblab.controller;

import com.weblab.dto.*;
import com.weblab.service.AuthService;
import com.weblab.util.RequestUtils;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/auth/sessions")
@RequiredArgsConstructor
@Slf4j
public class SessionController {

    private final AuthService authService;

    @GetMapping
    public ResponseEntity<List<SessionClosedDTO>> getSessions(HttpServletRequest request) {
        Long userId = RequestUtils.getUserId(request);
        Long currentSessionId = RequestUtils.getSessionId(request);

        List<SessionClosedDTO> sessions = authService.getUserSessions(userId, currentSessionId);
        return ResponseEntity.ok(sessions);
    }

    @DeleteMapping("/{sessionId}")
    public ResponseEntity<AuthResponse> closeSession(
            @PathVariable Long sessionId,
            HttpServletRequest request) {
        Long userId = RequestUtils.getUserId(request);
        Long currentSessionId = RequestUtils.getSessionId(request);

        authService.closeSession(sessionId, userId);

        boolean isCurrentSession = sessionId.equals(currentSessionId);

        return ResponseEntity.ok(
            AuthResponse.builder()
                .success(true)
                .message(isCurrentSession ? "Текущая сессия закрыта" : "Сессия закрыта")
                .isCurrentSession(isCurrentSession)
                .build()
        );
    }

    @PostMapping("/close-others")
    public ResponseEntity<AuthResponse> closeOtherSessions(HttpServletRequest request) {
        Long userId = RequestUtils.getUserId(request);
        Long currentSessionId = RequestUtils.getSessionId(request);

        int closed = authService.closeOtherSessions(userId, currentSessionId);

        return ResponseEntity.ok(
            AuthResponse.builder()
                .success(true)
                .message("Закрыто сессий: " + closed)
                .build()
        );
    }
}


