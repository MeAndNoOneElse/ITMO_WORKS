package com.weblab.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class LoginRequest {
    private String email;
    private String username;
    private String password;
    private String deviceName;
    private Integer expirationMinutes;

    private List<Long> sessionIdsToClose;
    private Long useExistingSessionId;
    private Boolean createNewSession;

    public String getUsername() {
        return (username == null || username.isEmpty()) ? email : username;
    }
}