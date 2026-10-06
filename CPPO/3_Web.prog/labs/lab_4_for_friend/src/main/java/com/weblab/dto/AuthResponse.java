package com.weblab.dto;

/**
 * Ответ на запросы аутентификации.
 */
public class AuthResponse {
    private boolean success;
    private String message;
    private String token;
    private String refreshToken;
    private UserDTO user;

    public AuthResponse() {}

    public AuthResponse(boolean success, String message) {
        this.success = success;
        this.message = message;
    }

    // ── getters/setters ───────────────────────────────────────────────────────

    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public String getToken() { return token; }
    public void setToken(String token) { this.token = token; }

    public String getRefreshToken() { return refreshToken; }
    public void setRefreshToken(String refreshToken) { this.refreshToken = refreshToken; }

    public UserDTO getUser() { return user; }
    public void setUser(UserDTO user) { this.user = user; }

    // ── Builder ───────────────────────────────────────────────────────────────

    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private final AuthResponse r = new AuthResponse();

        public Builder success(boolean v) { r.success = v; return this; }
        public Builder message(String v) { r.message = v; return this; }
        public Builder token(String v) { r.token = v; return this; }
        public Builder refreshToken(String v) { r.refreshToken = v; return this; }
        public Builder user(UserDTO v) { r.user = v; return this; }
        public AuthResponse build() { return r; }
    }

    // ── Inner UserDTO ─────────────────────────────────────────────────────────

    public static class UserDTO {
        private Long id;
        private String username;
        private String email;

        public UserDTO() {}

        public UserDTO(Long id, String username, String email) {
            this.id = id;
            this.username = username;
            this.email = email;
        }

        public Long getId() { return id; }
        public void setId(Long id) { this.id = id; }
        public String getUsername() { return username; }
        public void setUsername(String username) { this.username = username; }
        public String getEmail() { return email; }
        public void setEmail(String email) { this.email = email; }
    }
}

