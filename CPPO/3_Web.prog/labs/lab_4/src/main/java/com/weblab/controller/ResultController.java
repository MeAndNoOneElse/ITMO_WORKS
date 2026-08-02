package com.weblab.controller;

import com.weblab.dto.PointRequest;
import com.weblab.dto.ResultResponse;
import com.weblab.entity.User;
import com.weblab.service.ResultService;
import com.weblab.util.RequestUtils;
import jakarta.servlet.http.HttpServletRequest;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/results")
@RequiredArgsConstructor
public class ResultController {

    private final ResultService resultService;

    @PostMapping("/check")
    public ResponseEntity<?> checkPoint(@RequestBody PointRequest request, HttpServletRequest httpRequest) {
        Long userId = RequestUtils.getUserId(httpRequest);
        ResultResponse response = resultService.checkPoint(request, userId);
        return ResponseEntity.ok(response);
    }

    @GetMapping
    public ResponseEntity<?> getAllResults(HttpServletRequest httpRequest) {
        Long userId = RequestUtils.getUserId(httpRequest);
        List<ResultResponse> results = resultService.getAllResults(userId);
        return ResponseEntity.ok(results);
    }

    @DeleteMapping
    public ResponseEntity<?> clearResults(HttpServletRequest httpRequest) {
        Long userId = RequestUtils.getUserId(httpRequest);
        resultService.clearResults(userId);
        return ResponseEntity.ok(new ClearResultsResponse(true, "All results cleared successfully"));
    }

    @Data
    @AllArgsConstructor
    public static class ClearResultsResponse {
        private boolean success;
        private String message;
    }
}

