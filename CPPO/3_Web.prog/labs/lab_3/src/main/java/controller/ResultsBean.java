package controller;

import dto.ResultDTO;

import jakarta.annotation.PostConstruct;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.inject.Named;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

import service.AreaCheckServiceInterface;
import service.CacheType;
import service.CachingAreaCheckService;

@Named
@ApplicationScoped
public class ResultsBean implements Serializable {

    @Inject
    private CachingAreaCheckService cacheController;

    private List<ResultDTO> results = new ArrayList<>();

    @PostConstruct
    public void init() {
        loadResultsFromDatabase();
    }

    private void loadResultsFromDatabase() {
        results.clear();
        AreaCheckServiceInterface svc = cacheController.getService();
        results.addAll(svc.getAllResults());
    }

    public List<ResultDTO> getResults() {
        return results;
    }

    public void addResult(ResultDTO result) {
        results.add(0, result); // добавляем в начало списка
    }

    public void clearResults() {
        cacheController.deleteAllEverything();
        results.clear();
    }

    public CacheType getCacheType() {
        return cacheController.getCacheType();
    }
}
