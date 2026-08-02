package service;

import dto.PointDTO;
import dto.ResultDTO;
import jakarta.annotation.PostConstruct;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import service.cache.CacheProvider;
import service.cache.CaffeineCacheProvider;
import service.cache.RedisCacheProvider;

import java.io.Serializable;
import java.util.Collections;
import java.util.List;
import java.util.logging.Logger;

@ApplicationScoped
public class CachingAreaCheckService implements AreaCheckServiceInterface, Serializable {

    private static final Logger LOGGER = Logger.getLogger(CachingAreaCheckService.class.getName());

    @Inject
    @PlainService
    private AreaCheckServiceInterface baseService;

    @Inject
    private CaffeineCacheProvider caffeineProvider;

    @Inject
    private RedisCacheProvider redisProvider;

    private volatile CacheType currentCacheType = CacheType.CAFFEINE;

    private volatile CacheProvider activeProvider;

    @PostConstruct
    public void init() {
        updateActiveProvider();
        LOGGER.info("[CACHE] CachingAreaCheckService initialized with cache type: " + currentCacheType);
    }


    public CacheType getCacheType() {
        return currentCacheType;
    }

    public void setCacheType(CacheType type) {
        CacheType oldType = this.currentCacheType;
        this.currentCacheType = (type == null) ? CacheType.CAFFEINE : type;
        updateActiveProvider();
        LOGGER.info(() -> String.format("[CACHE] Cache type changed from %s to %s", oldType, this.currentCacheType));

        if (activeProvider != null) {
            activeProvider.invalidate();
            LOGGER.fine("[CACHE] Active provider invalidated after type switch");
        }
    }

    private void updateActiveProvider() {
        if (currentCacheType == CacheType.CAFFEINE) {
            activeProvider = caffeineProvider;
        } else if (currentCacheType == CacheType.REDIS) {
            activeProvider = redisProvider;
        } else {
            activeProvider = caffeineProvider; // fallback
        }
        LOGGER.fine(() -> "[CACHE] Active provider set to: " +
                (activeProvider != null ? activeProvider.getClass().getSimpleName() : "null"));
    }

    public AreaCheckServiceInterface getService() {
        return this;
    }


    public void invalidateAllCaches() {
        LOGGER.info("[CACHE] invalidateAllCaches() called");
        if (caffeineProvider != null) {
            caffeineProvider.invalidate();
            LOGGER.fine("[CACHE] Caffeine cache invalidated");
        }
        if (redisProvider != null) {
            redisProvider.invalidate();
            LOGGER.fine("[CACHE] Redis cache invalidated");
        }
    }

    public void deleteAllEverything() {
        LOGGER.info("[CACHE] deleteAllEverything() called — deleting from DB and invalidating all caches");

        if (baseService != null) {
            try {
                baseService.deleteAllResults();
                LOGGER.info("[CACHE] All results deleted from DB");
            } catch (Exception e) {
                LOGGER.warning("[CACHE] Error deleting all results from DB: " + e);
            }
        } else {
            LOGGER.warning("[CACHE] baseService is null in deleteAllEverything()");
        }

        invalidateAllCaches();
        LOGGER.fine("[CACHE] deleteAllEverything() completed");
    }


    @Override
    public ResultDTO checkAndSave(PointDTO point) {
        LOGGER.fine("[CACHE] checkAndSave() — delegating to baseService");

        if (baseService == null) {
            LOGGER.severe("[CACHE] baseService is not available in checkAndSave()");
            throw new IllegalStateException("baseService not available");
        }

        ResultDTO result = baseService.checkAndSave(point);

        if (activeProvider != null) {
            String providerName = activeProvider.getClass().getSimpleName();
            LOGGER.info(() -> "[CACHE] Invalidating " + providerName + " after new data saved");
            activeProvider.invalidate();
        }

        return result;
    }

    @Override
    public List<ResultDTO> getAllResults() {
        if (baseService == null) {
            LOGGER.warning("[CACHE] baseService is null — returning empty list");
            return Collections.emptyList();
        }

        CacheProvider provider = this.activeProvider;

        if (provider == null) {
            LOGGER.fine("[CACHE] No active provider — loading from DB");
            return loadFromDatabase("no cache");
        }

        String providerName = provider.getClass().getSimpleName();

        List<ResultDTO> cached = provider.get();
        if (cached != null && provider.isFresh()) {
            LOGGER.info(() -> String.format("[CACHE] HIT (%s) — returning %d rows from cache",
                    providerName, cached.size()));
            return cached;
        }

        LOGGER.info(() -> "[CACHE] MISS (" + providerName + ") — loading from DB");
        List<ResultDTO> fromDb = loadFromDatabase(providerName);

        provider.put(fromDb);
        LOGGER.info(() -> String.format("[CACHE] Updated %s with %d rows from DB",
                providerName, fromDb.size()));

        return fromDb;
    }

    private List<ResultDTO> loadFromDatabase(String context) {
        try {
            List<ResultDTO> data = baseService.getAllResults();
            LOGGER.info(() -> String.format("[DB] Loaded %d rows from database (context=%s)",
                    data.size(), context));
            return data;
        } catch (Exception e) {
            LOGGER.warning("[CACHE] Failed to load from DB: " + e);
            return Collections.emptyList();
        }
    }

    @Override
    public void deleteAllResults() {
        deleteAllEverything();
    }
}
