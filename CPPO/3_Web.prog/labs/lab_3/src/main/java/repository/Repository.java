package repository;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.transaction.Transactional;
import entity.ResultEntity;

import java.util.List;

@ApplicationScoped
public class Repository implements RepositoryInterface {

    @PersistenceContext(unitName = "labPU")
    private EntityManager entityManager;

    @Override
    @Transactional
    public void saveResult(ResultEntity point) {
        entityManager.persist(point);
    }

    @Override
    public List<ResultEntity> getAllPoints() {
        return entityManager.createQuery(
                "SELECT p FROM ResultEntity p ORDER BY p.timestamp DESC",
                ResultEntity.class
        ).getResultList();
    }

    @Override
    @Transactional
    public void deleteAllPoints() {
        entityManager.createQuery("DELETE FROM ResultEntity").executeUpdate();
    }
}