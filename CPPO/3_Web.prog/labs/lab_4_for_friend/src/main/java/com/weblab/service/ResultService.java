package com.weblab.service;

import com.weblab.dto.PointRequest;
import com.weblab.dto.ResultResponse;
import com.weblab.entity.UserEntity;
import com.weblab.repository.ResultRepository;
import com.weblab.repository.UserRepository;
import com.weblab.util.HitChecker;

import java.util.List;

/**
 * Сервис работы с результатами (точками).
 */
public class ResultService {

    private final ResultRepository repo     = new ResultRepository();
    private final UserRepository   userRepo = new UserRepository();

    public ResultResponse checkPoint(PointRequest req, long userId) {
        if (req.getX() == null || req.getY() == null || req.getR() == null)
            throw new IllegalArgumentException("x, y, r обязательны");

        UserEntity user = userRepo.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("Пользователь не найден"));

        long startNano = System.nanoTime();
        boolean hit = HitChecker.isHit(req.getX(), req.getY(), req.getR());
        long execMicros = (System.nanoTime() - startNano) / 1000;

        return repo.save(user, req.getX(), req.getY(), req.getR(), hit, execMicros);
    }

    public List<ResultResponse> getAll(long userId) {
        return repo.findByUserId(userId);
    }

    public void clearAll(long userId) {
        repo.deleteByUserId(userId);
    }
}
