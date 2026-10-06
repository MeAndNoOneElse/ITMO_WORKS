package com.weblab.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class ResultResponse {
    private Long id;
    private Double x;
    private Double y;
    private Double r;
    private Boolean hit;
    private String createdAt;
    private Long executionTime;
}

