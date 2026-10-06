package com.weblab.dto;

import com.weblab.entity.Session;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SessionClosedDTO {
    private Long id;
    private String deviceName;
    private String ipAddress;
    private LocalDateTime createdAt;
    private LocalDateTime refreshExpiresAt;

    public static SessionClosedDTO fromSession(Session session) {
        return new SessionClosedDTO(
                session.getId(),
                session.getDeviceName(),
                session.getIpAddress(),
                session.getCreatedAt(),
                session.getRefreshExpiresAt()
        );
    }

    public static List<SessionClosedDTO> fromSessions(List<Session> sessions) {
        return sessions.stream()
                .map(SessionClosedDTO::fromSession)
                .collect(Collectors.toList());
    }
}

