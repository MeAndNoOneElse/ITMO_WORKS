package service.cache;

import dto.ResultDTO;

import jakarta.enterprise.context.ApplicationScoped;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;

@ApplicationScoped
public class RedisCacheProvider implements CacheProvider {

    private volatile List<ResultDTO> cached;
    private final AtomicLong timestamp = new AtomicLong(0);
    private final long ttlMillis = 1_000_000;
    @Override
    public List<ResultDTO> get() {
        if (!isFresh()) return null;
        return new ArrayList<>(cached);
    }

    @Override
    public void put(List<ResultDTO> data) {
        if (data == null) {
            invalidate();
            return;
        }
        this.cached = new ArrayList<>(data);
        this.timestamp.set(System.currentTimeMillis());
    }

    @Override
    public void invalidate() {
        this.cached = null;
        this.timestamp.set(0);
    }

    @Override
    public boolean isFresh() {
        List<ResultDTO> loc = this.cached;
        if (loc == null) return false;
        long ts = this.timestamp.get();
        return ts > 0 && (System.currentTimeMillis() - ts) <= ttlMillis;
    }
}

