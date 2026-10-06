package com.weblab.repository;

import com.weblab.entity.Session;
import com.weblab.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface SessionRepository extends JpaRepository<Session, Long> {

    @Query("SELECT s FROM Session s WHERE s.user = :user AND s.status = 'OPEN'")
    List<Session> findOpenSessionsByUser(@Param("user") User user);

    @Query("SELECT s FROM Session s WHERE s.user = :user AND s.status = 'OPEN' AND s.id != :sessionId")
    List<Session> findOpenSessionsByUserExceptCurrent(@Param("user") User user, @Param("sessionId") Long sessionId);


    @Modifying
    @Transactional
    @Query("UPDATE Session s SET s.status = 'CLOSED' WHERE s.id = :sessionId AND s.user.id = :userId")
    int closeSessionByIdAndUserId(@Param("sessionId") Long sessionId, @Param("userId") Long userId);

    @Modifying
    @Transactional
    @Query("UPDATE Session s SET s.status = 'CLOSED' WHERE s.user.id = :userId AND s.id != :currentSessionId AND s.status = 'OPEN'")
    int closeOtherSessions(@Param("userId") Long userId, @Param("currentSessionId") Long currentSessionId);

    @Modifying
    @Transactional
    @Query("UPDATE Session s SET s.status = 'CLOSED' " +
           "WHERE s.status = 'OPEN' AND s.refreshExpiresAt < :cutoffTime")
    int closeExpiredSessions(@Param("cutoffTime") LocalDateTime cutoffTime);
}

