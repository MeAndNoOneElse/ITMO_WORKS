package com.weblab.util;

import com.weblab.entity.User;
import com.weblab.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.stereotype.Component;

@Component
public class RequestUtils {

    private static UserService userService;

    public RequestUtils(UserService userService) {
        RequestUtils.userService = userService;
    }

    public static Long getUserId(HttpServletRequest request) {
        Object userIdAttr = request.getAttribute("userId");
        return userIdAttr instanceof Long ? (Long) userIdAttr : null;
    }

    public static Long getSessionId(HttpServletRequest request) {
        Object sessionIdAttr = request.getAttribute("sessionId");
        return sessionIdAttr instanceof Long ? (Long) sessionIdAttr : null;
    }

    public static String extractIpAddress(String xForwardedFor) {
        return xForwardedFor != null ? xForwardedFor.split(",")[0].trim() : "localhost";
    }
}
