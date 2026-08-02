package com.weblab.service;

import com.weblab.entity.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Service
@Slf4j
public class ResultCacheService {

    private static final int MAX_CACHED_RESULTS_PER_USER = 100;

    private final Map<Long, LinkedList<Result>> userResultsCache = new ConcurrentHashMap<>();

    private long cacheHits = 0;
    private long cacheMisses = 0;

    public void addResult(Result result) {
        Long userId = result.getUser().getId();

        userResultsCache.compute(userId, (key, existingList) -> {
            LinkedList<Result> list = (existingList != null) ? existingList : new LinkedList<>();

            list.addFirst(result);

            if (list.size() > MAX_CACHED_RESULTS_PER_USER) {
                list.removeLast();
            }

            log.debug("Результат добавлен в кеш для пользователя {} (размер кеша: {})",
                    userId, list.size());

            return list;
        });
    }

    public List<Result> getResults(Long userId) {
        log.debug("Запрос кеша для userId={}, текущие ключи в кеше: {}", userId, userResultsCache.keySet());

        LinkedList<Result> cached = userResultsCache.get(userId);

        if (cached != null) {
            cacheHits++;

            if (cached.isEmpty()) {
                log.info("CACHE HIT: Пустой список из кеша (0 DB запросов) | " +
                        "Попаданий: {}, Промахов: {}",
                        cacheHits, cacheMisses);
            } else {
                log.info("CACHE HIT: Результаты взяты из кеша (0 DB запросов) | " +
                        "Кеш содержит {} элементов | Попаданий: {}, Промахов: {}",
                        cached.size(), cacheHits, cacheMisses);
            }

            return new ArrayList<>(cached);
        }

        cacheMisses++;
        log.debug("CACHE MISS: Кеш не инициализирован для userId={}, нужно загрузить из БД | " +
                "Попаданий: {}, Промахов: {}", userId, cacheHits, cacheMisses);

        return null;
    }

    public void initCache(Long userId, List<Result> results) {
        LinkedList<Result> list = new LinkedList<>();

        int count = Math.min(results.size(), MAX_CACHED_RESULTS_PER_USER);
        for (int i = 0; i < count; i++) {
            list.add(results.get(i));
        }

        userResultsCache.put(userId, list);

        log.info("Кеш инициализирован для пользователя {} ({} результатов). Всего пользователей в кеше: {}",
                userId, list.size(), userResultsCache.size());
    }

    public void clearCache(Long userId) {
        userResultsCache.remove(userId);
        log.info("Кеш очищен для пользователя {}. Осталось пользователей в кеше: {}",
                userId, userResultsCache.size());
    }

}

