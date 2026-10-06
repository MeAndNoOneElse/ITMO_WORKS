package controller;

import java.io.Serializable;

import jakarta.enterprise.context.SessionScoped;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import service.CacheType;
import service.CachingAreaCheckService;

@Named("cacheSwitcher")
@SessionScoped
public class CacheSwitcherBean implements Serializable {
    private static final long serialVersionUID = 1L;

    @Inject
    private CachingAreaCheckService cacheService;

    public CacheType getCurrent() {
        return cacheService.getCacheType();
    }

    public CacheType getCurrentCache() {
        return cacheService.getCacheType();
    }

    public CacheType[] getAvailableCaches() {
        return CacheType.values();
    }

    public void setCache(CacheType type) {
        if (type == null) return;
        cacheService.setCacheType(type);
    }

    public void setCaffeine() {
        setCache(CacheType.CAFFEINE);
    }

    public void setRedis() {
        setCache(CacheType.REDIS);
    }

    public String getCurrentCacheLabel() {
        return getCurrentCache() != null ? getCurrentCache().name() : "UNKNOWN";
    }
}
