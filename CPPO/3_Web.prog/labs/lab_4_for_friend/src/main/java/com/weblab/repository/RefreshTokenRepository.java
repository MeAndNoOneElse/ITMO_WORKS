package com.weblab.repository;

import com.weblab.db.Database;
import com.weblab.entity.RefreshTokenEntity;
import com.weblab.entity.UserEntity;
import jakarta.persistence.EntityManager;
import jakarta.persistence.NoResultException;

import java.util.Optional;

/**
 * Репозиторий refresh-токенов (JPA).
 */
public class RefreshTokenRepository {

    public void save(UserEntity user, String token, long expiresAt) {
        // Одна активная сессия — удаляем старые токены пользователя
        deleteByUser(user);
        EntityManager em = Database.createEntityManager();
        try {
            em.getTransaction().begin();
            em.persist(new RefreshTokenEntity(user, token, expiresAt));
            em.getTransaction().commit();
        } catch (Exception e) {
            if (em.getTransaction().isActive()) em.getTransaction().rollback();
            throw new RuntimeException(e);
        } finally {
            em.close();
        }
    }

    public Optional<Long> findUserIdByToken(String token) {
        EntityManager em = Database.createEntityManager();
        try {
            RefreshTokenEntity rt = em.createQuery(
                    "SELECT t FROM RefreshTokenEntity t WHERE t.token = :tok",
                    RefreshTokenEntity.class)
                    .setParameter("tok", token)
                    .getSingleResult();
            if (System.currentTimeMillis() < rt.getExpiresAt()) {
                return Optional.of(rt.getUser().getId());
            }
            return Optional.empty();
        } catch (NoResultException e) {
            return Optional.empty();
        } finally {
            em.close();
        }
    }

    public void deleteByToken(String token) {
        EntityManager em = Database.createEntityManager();
        try {
            em.getTransaction().begin();
            em.createQuery("DELETE FROM RefreshTokenEntity t WHERE t.token = :tok")
              .setParameter("tok", token)
              .executeUpdate();
            em.getTransaction().commit();
        } catch (Exception e) {
            if (em.getTransaction().isActive()) em.getTransaction().rollback();
            throw new RuntimeException(e);
        } finally {
            em.close();
        }
    }

    public void deleteByUserId(long userId) {
        EntityManager em = Database.createEntityManager();
        try {
            em.getTransaction().begin();
            em.createQuery("DELETE FROM RefreshTokenEntity t WHERE t.user.id = :uid")
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

    private void deleteByUser(UserEntity user) {
        deleteByUserId(user.getId());
    }
}
