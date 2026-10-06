package service;

import dto.ResultDTO;
import dto.PointDTO;

import entity.ResultEntity;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import repository.RepositoryInterface;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.logging.Logger;

@PlainService
@ApplicationScoped
public class AreaCheckService implements AreaCheckServiceInterface, Serializable {

    private static final Logger LOGGER = Logger.getLogger(AreaCheckService.class.getName());

    @Inject
    private RepositoryInterface repository;

    @Override
    public ResultDTO checkAndSave(PointDTO point) {
        long startTime = System.nanoTime();
        boolean hit = checkHit(point.getX(), point.getY(), point.getR());
        long endTime = System.nanoTime();
        long executionTimeNano = endTime - startTime;
        long executionTimeMillis = executionTimeNano/1000;
        Date date = new Date();

        ResultDTO resultDTO = new ResultDTO(point.getX(), point.getY(), point.getR(), hit, date, executionTimeMillis);

        ResultEntity result = new ResultEntity(1, point.getX(), Double.parseDouble(point.getY()), point.getR(), hit, date, executionTimeMillis);

        LOGGER.info(() -> String.format("[DB] saveResult() called — saving new result: x=%.4f, y=%s, r=%.4f, hit=%b, execMs=%d",
                point.getX(), point.getY(), point.getR(), hit, executionTimeMillis));

        repository.saveResult(result);

        LOGGER.fine("[DB] saveResult() completed");

        return resultDTO;
    }

    @Override
    public List<ResultDTO> getAllResults() {
        if (repository == null) {
            LOGGER.warning("[DB] repository is null in getAllResults() — returning empty list to avoid NPE during init");
            return new ArrayList<>();
        }

        LOGGER.info("[DB] getAllPoints() called — fetching from database at " + new Date());

        List<ResultEntity> entities = repository.getAllPoints();

        int rows = (entities == null) ? 0 : entities.size();
        LOGGER.info(() -> String.format("[DB] Loaded %d rows from database (source=DB)", rows));

        List<ResultDTO> results = new ArrayList<>();
        for (ResultEntity entity : entities) {
            long execMs = entity.getExecutionTimeNano()/1_000_000_000;
            ResultDTO dto = new ResultDTO(
                entity.getX(),
                String.valueOf(entity.getY()),
                entity.getR(),
                entity.isHit(),
                entity.getTimestamp(),
                execMs
            );
            results.add(dto);
        }
        LOGGER.fine(() -> String.format("[DB] getAllPoints() returned %d rows", results.size()));
        return results;
    }

    @Override
    public void deleteAllResults() {
        LOGGER.info("[DB] deleteAllPoints() called — deleting all results from DB");

        repository.deleteAllPoints();

        LOGGER.fine("[DB] deleteAllPoints() completed");
    }

    private boolean checkHit(double x, String yStr, double r) {
        double y;
        try {
            y = Double.parseDouble(yStr);
        } catch (Exception e) {
            return false;
        }
        if (x >= 0 && y >= 0) {
            return x <= r && y <= r / 2;
        }
        if (x <= 0 && y >= 0) {
            return y <= x + r / 2;
        }
        if (x >= 0 && y <= 0) {
            return (x * x + y * y) <= (r * r);
        }
        return false;
    }


}