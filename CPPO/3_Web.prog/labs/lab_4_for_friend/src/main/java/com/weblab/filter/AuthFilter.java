package com.weblab.filter;

import com.weblab.util.JwtUtil;
import io.jsonwebtoken.Claims;
import jakarta.annotation.Priority;
import jakarta.ws.rs.Priorities;
import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.container.ContainerRequestFilter;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.core.SecurityContext;
import jakarta.ws.rs.ext.Provider;

import java.io.IOException;
import java.security.Principal;

/**
 * Фильтр JWT-аутентификации.
 * Проверяет Bearer-токен и помещает userId в property запроса.
 * Не блокирует эндпоинты /api/auth/* — они публичные.
 */
@Provider
@Priority(Priorities.AUTHENTICATION)
public class AuthFilter implements ContainerRequestFilter {

    @Override
    public void filter(ContainerRequestContext ctx) throws IOException {
        String path = ctx.getUriInfo().getPath();

        // Публичные маршруты — пропускаем
        if (path.startsWith("api/auth/") || path.startsWith("/api/auth/")) {
            return;
        }

        String authHeader = ctx.getHeaderString("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            ctx.abortWith(unauthorized("Токен отсутствует"));
            return;
        }

        String token = authHeader.substring("Bearer ".length()).trim();
        try {
            Claims claims = JwtUtil.validateAccessToken(token);
            long userId = JwtUtil.getUserId(claims);
            String username = JwtUtil.getUsername(claims);

            // Сохраняем userId в свойствах запроса
            ctx.setProperty("userId", userId);
            ctx.setProperty("username", username);

            // Устанавливаем SecurityContext
            ctx.setSecurityContext(new SecurityContext() {
                @Override
                public Principal getUserPrincipal() {
                    return () -> username;
                }
                @Override
                public boolean isUserInRole(String role) { return false; }
                @Override
                public boolean isSecure() { return ctx.getSecurityContext().isSecure(); }
                @Override
                public String getAuthenticationScheme() { return "Bearer"; }
            });

        } catch (Exception e) {
            ctx.abortWith(unauthorized("Токен недействителен или истёк"));
        }
    }

    private Response unauthorized(String msg) {
        return Response.status(Response.Status.UNAUTHORIZED)
                .entity("{\"success\":false,\"message\":\"" + msg + "\"}")
                .type("application/json")
                .build();
    }
}

