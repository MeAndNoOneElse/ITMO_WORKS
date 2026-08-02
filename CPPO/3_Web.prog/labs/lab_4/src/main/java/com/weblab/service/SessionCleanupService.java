package com.weblab.service;

import com.weblab.repository.SessionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
@Slf4j
public class SessionCleanupService {

    private final SessionRepository sessionRepository;

    @Scheduled(fixedRate = 2 * 60 * 60 * 1000, initialDelay = 20000)
    @Transactional
    public void cleanupExpiredSessions() {
        log.info("Начинается очистка истёкших сессий (refresh_expires_at > 2 часов назад)...");

        try {
            LocalDateTime cutoffTime = LocalDateTime.now().minusHours(2);

            int closedCount = sessionRepository.closeExpiredSessions(cutoffTime);

            if (closedCount > 0) {
                log.info("Закрыто {} истёкших сессий одним запросом (экономия {} DB запросов)",
                    closedCount, closedCount);
            } else {
                log.info("Нет сессий для закрытия (все ещё в периоде 2 часов после экспирации)");
            }

        } catch (Exception e) {
            log.error("Ошибка при очистке сессий: {}", e.getMessage(), e);
        }
    }
}





