package com.weblab.dto;

import com.weblab.entity.User;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AuthResponse {
    private boolean success;
    private String message;
    private UserDTO user;
    private String token;
    private String refreshToken;
    private Long sessionId; // ID текущей сессии
    private List<SessionClosedDTO> closedSessions;
    private List<SessionClosedDTO> activeSessions;
    private boolean hasActiveSessions;
    private boolean isCurrentSession;

    public AuthResponse(boolean success, String message, UserDTO user, String token) {
        this.success = success;
        this.message = message;
        this.user = user;
        this.token = token;
        this.closedSessions = null;
        this.activeSessions = null;
        this.hasActiveSessions = false;
    }


    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class UserDTO {
        private Long id;
        private String email;
        private String username;
        private Long createdAt;

        public static UserDTO fromUser(User user) {
            return new UserDTO(
                    user.getId(),
                    user.getEmail(),
                    user.getUsername(),
                    user.getCreatedAt()
            );
        }
    }
}