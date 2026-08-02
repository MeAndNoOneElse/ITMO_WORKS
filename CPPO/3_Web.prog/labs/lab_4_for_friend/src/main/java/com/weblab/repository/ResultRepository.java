package com.weblab.repository;

import com.weblab.db.Database;
import com.weblab.dto.ResultResponse;
import com.weblab.entity.PointEntity;
import com.weblab.entity.UserEntity;
import jakarta.persistence.EntityManager;

import java.util.List;

/**
 * Репозиторий точек (JPA).
 */
public class ResultRepository {

    public ResultResponse save(UserEntity user, double x, double y, double r,
                               boolean hit, long executionTime) {
        EntityManager em = Database.createEntityManager();
        try {
            em.getTransaction().begin();
            PointEntity p = new PointEntity(user, x, y, r, hit, executionTime);
            em.persist(p);
            em.getTransaction().commit();
            return toResponse(p);
        } catch (Exception e) {
            if (em.getTransaction().isActive()) em.getTransaction().rollback();
            throw new RuntimeException(e);
        } finally {
            em.close();
        }
    }

    public List<ResultResponse> findByUserId(long userId) {
        EntityManager em = Database.createEntityManager();
        try {
            return em.createQuery(
                    "SELECT p FROM PointEntity p WHERE p.user.id = :uid ORDER BY p.id DESC",
                    PointEntity.class)
                    .setParameter("uid", userId)
                    .getResultList()
                    .stream()
                    .map(ResultRepository::toResponse)
                    .toList();
        } finally {
            em.close();
        }
    }

    public void deleteByUserId(long userId) {
        EntityManager em = Database.createEntityManager();
        try {
            em.getTransaction().begin();
            em.createQuery("DELETE FROM PointEntity p WHERE p.user.id = :uid")
              .setParameter("uid", userId)
              .executeUpdate();
            em.getTransaction().commit();
        } catch (Exception e) {
            if (em.getTransaction().isActive()) em.getTransaction().rollback();
            throw new RuntimeException(e);
        } finally {
            em.close();
        }
    }

    private static ResultResponse toResponse(PointEntity p) {
        // Отдаём createdAtEpoch — фронт использует new Date(epochMilli)
        return new ResultResponse(p.getId(), p.getX(), p.getY(), p.getR(),
                p.getHit(), p.getCreatedAtEpoch(), p.getExecutionTime());
    }
}
