package repository;

import entity.ResultEntity;

import java.util.List;

public interface RepositoryInterface {
    void saveResult(ResultEntity point);
    List<ResultEntity> getAllPoints();
    void deleteAllPoints();
}

