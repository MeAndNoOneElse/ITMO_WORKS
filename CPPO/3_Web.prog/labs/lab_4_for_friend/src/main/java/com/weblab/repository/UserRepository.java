package com.weblab.repository;

import com.weblab.db.Database;
import com.weblab.entity.UserEntity;
import jakarta.persistence.EntityManager;
import jakarta.persistence.NoResultException;

import java.util.Optional;

/**
 * Репозиторий пользователей (JPA).
 */
public class UserRepository {

    public Optional<UserEntity> findByUsername(String username) {
        EntityManager em = Database.createEntityManager();
        try {
            UserEntity u = em.createQuery(
                    "SELECT u FROM UserEntity u WHERE u.username = :name", UserEntity.class)
                    .setParameter("name", username)
                    .getSingleResult();
            return Optional.of(u);
        } catch (NoResultException e) {
            return Optional.empty();
        } finally {
            em.close();
        }
    }

    public Optional<UserEntity> findById(long id) {
        EntityManager em = Database.createEntityManager();
        try {
            return Optional.ofNullable(em.find(UserEntity.class, id));
        } finally {
            em.close();
        }
    }

    public UserEntity create(String username, String email, String passwordHash) {
        EntityManager em = Database.createEntityManager();
        try {
            em.getTransaction().begin();
            UserEntity u = new UserEntity(username, email, passwordHash);
            em.persist(u);
            em.getTransaction().commit();
            return u;
        } catch (Exception e) {
            if (em.getTransaction().isActive()) em.getTransaction().rollback();
            throw new RuntimeException(e);
        } finally {
            em.close();
        }
    }

    public boolean existsByUsername(String username) {
        EntityManager em = Database.createEntityManager();
        try {
            Long count = em.createQuery(
                    "SELECT COUNT(u) FROM UserEntity u WHERE u.username = :name", Long.class)
                    .setParameter("name", username)
                    .getSingleResult();
            return count > 0;
        } finally {
            em.close();
        }
    }
}
