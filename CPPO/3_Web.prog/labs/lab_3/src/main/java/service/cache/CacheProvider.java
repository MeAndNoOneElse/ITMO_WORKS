package service.cache;

import dto.ResultDTO;

import java.util.List;

public interface CacheProvider {
    List<ResultDTO> get();
    void put(List<ResultDTO> data);
    void invalidate();
    boolean isFresh();
}

