package service;

import dto.PointDTO;
import dto.ResultDTO;

import java.util.List;

public interface AreaCheckServiceInterface {
    ResultDTO checkAndSave(PointDTO point);
    List<ResultDTO> getAllResults();
    void deleteAllResults();
}

