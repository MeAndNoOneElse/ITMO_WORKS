package com.weblab.service;

import com.weblab.dto.PointRequest;
import com.weblab.dto.ResultResponse;
import com.weblab.entity.Result;
import com.weblab.entity.User;
import com.weblab.repository.ResultRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;

import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class ResultService {

    private final ResultRepository resultRepository;
    private final ResultCacheService resultCacheService;
    private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    @Transactional
    public ResultResponse checkPoint(PointRequest request, Long userId) {
        log.debug("ResultService.checkPoint() вызван для точки ({}, {}, {})",
                request.getX(), request.getY(), request.getR());

        if (request.getX() == null || request.getY() == null || request.getR() == null) {
            throw new IllegalArgumentException("Все параметры должны быть заполнены");
        }

        double x = request.getX();
        double y = request.getY();
        double r = request.getR();

        if (r <= 0) {
            throw new IllegalArgumentException("R должен быть положительным");
        }

        long startTime = System.nanoTime();

        boolean hit = checkHit(x, y, r);

        long executionTime = (System.nanoTime() - startTime) / 1000;

        User user = new User();
        user.setId(userId);

        Result result = new Result();
        result.setX(x);
        result.setY(y);
        result.setR(r);
        result.setHit(hit);
        result.setExecutionTime(executionTime);
        result.setUser(user);

        log.debug("Будет выполнен DB запрос: INSERT INTO results");
        result = resultRepository.save(result);
        log.info("Результат проверки точки сохранён (hit={}) → Выполнено: 1 DB запрос (INSERT)", hit);
// тут есть транзакция, чтобы не получилось грязных данных в кеше
        Result finalResult = result;
        TransactionSynchronizationManager.registerSynchronization(
            new TransactionSynchronization() {
                @Override
                public void afterCommit() {
                    resultCacheService.addResult(finalResult);
                    log.debug("Результат добавлен в кеш ПОСЛЕ коммита транзакции для пользователя {}", userId);
                }

                @Override
                public void afterCompletion(int status) {
                    if (status == STATUS_ROLLED_BACK) {
                        log.warn("Транзакция откачена - результат НЕ добавлен в кеш (данные согласованы)");
                    }
                }
            }
        );

        return toResponse(result);
    }


    private boolean checkHit(double x, double y, double r) {
        if (x >= 0 && y >= 0) {
            return x <= r / 2 && y <= r;
        }

        if (x <= 0 && y >= 0) {
            return (x * x + y * y) <= (r * r);
        }

        if (x <= 0 && y <= 0) {
            return false;
        }

        if (x >= 0 && y <= 0) {
            return y >= 2 * x - r;
        }

        return false;
    }

    @Transactional(readOnly = true)
    public List<ResultResponse> getAllResults(Long userId) {
        log.debug("ResultService.getAllResults() вызван для пользователя: {}", userId);

        List<Result> results = resultCacheService.getResults(userId);

        if (results != null) {
            log.info("Результаты взяты из кеша → Выполнено: 0 DB запросов | Кеш: {} результатов",
                    results.size());

            return results.stream()
                    .map(this::toResponse)
                    .collect(Collectors.toList());
        }

        User user = new User();
        user.setId(userId);

        log.debug("Будет выполнен DB запрос: SELECT results WHERE user_id ORDER BY created_at DESC");
        results = resultRepository.findByUserOrderByCreatedAtDesc(user);

        resultCacheService.initCache(userId, results);

        log.info("Получено {} результатов из БД и кеш инициализирован → Выполнено: 1 DB запрос (SELECT)",
                results.size());

        return results.stream()
                .map(this::toResponse)
                .collect(Collectors.toList());
    }

    @Transactional
    public void clearResults(Long userId) {
        log.debug("ResultService.clearResults() вызван для пользователя: {}", userId);

        User user = new User();
        user.setId(userId);

        log.debug("Будет выполнен DB запрос: DELETE FROM results WHERE user_id");

        int deletedCount = resultRepository.deleteAllByUser(user);

        log.info("Удалено {} результатов из БД → Выполнено: 1 DB запрос (DELETE)", deletedCount);


        TransactionSynchronizationManager.registerSynchronization(
            new TransactionSynchronization() {
                @Override
                public void afterCommit() {
                    resultCacheService.clearCache(userId);
                    log.debug("Кеш очищен ПОСЛЕ коммита транзакции для пользователя {}", userId);
                }

                @Override
                public void afterCompletion(int status) {
                    if (status == STATUS_ROLLED_BACK) {
                        log.warn("Транзакция откачена - кеш НЕ очищен (данные согласованы)");
                    }
                }
            }
        );
    }

    private ResultResponse toResponse(Result result) {
        return new ResultResponse(
                result.getId(),
                result.getX(),
                result.getY(),
                result.getR(),
                result.getHit(),
                result.getCreatedAt().format(FORMATTER),
                result.getExecutionTime()
        );
    }
}

