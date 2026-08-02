package service.cache;

import dto.ResultDTO;

import jakarta.enterprise.context.ApplicationScoped;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;
import java.util.logging.Logger;

@ApplicationScoped
public class CaffeineCacheProvider implements CacheProvider {

    private static final Logger LOGGER = Logger.getLogger(CaffeineCacheProvider.class.getName());

    private volatile List<ResultDTO> cached;
    private final AtomicLong timestamp = new AtomicLong(0);
    private final long ttlMillis = 1_000_000;

    @Override
    public List<ResultDTO> get() {
        if (!isFresh()) {
            LOGGER.fine("[Caffeine] get() -> cache miss or stale");
            return null;
        }
        LOGGER.fine(() -> String.format("[Caffeine] get() -> cache hit, rows=%d", cached != null ? cached.size() : 0));
        return new ArrayList<>(cached);
    }

    @Override
    public void put(List<ResultDTO> data) {
        if (data == null) {
            LOGGER.fine("[Caffeine] put(null) -> invalidate cache");
            invalidate();
            return;
        }
        this.cached = new ArrayList<>(data);
        this.timestamp.set(System.currentTimeMillis());
        LOGGER.info(() -> String.format("[Caffeine] put() -> cached %d rows (ts=%d)", data.size(), this.timestamp.get()));
    }

    @Override
    public void invalidate() {
        this.cached = null;
        this.timestamp.set(0);
        LOGGER.info("[Caffeine] invalidate() -> cache cleared");
    }

    @Override
    public boolean isFresh() {
        List<ResultDTO> loc = this.cached;
        if (loc == null) {
            return false;
        }
        long ts = this.timestamp.get();
        boolean fresh = ts > 0 && (System.currentTimeMillis() - ts) <= ttlMillis;
        LOGGER.finer(() -> String.format("[Caffeine] isFresh() -> %b (age=%d ms)", fresh, System.currentTimeMillis() - ts));
        return fresh;
    }
}
