package com.weblab.resource;

import com.weblab.dto.AuthResponse;
import com.weblab.dto.LoginRequest;
import com.weblab.dto.RefreshTokenRequest;
import com.weblab.dto.RegisterRequest;
import com.weblab.service.AuthService;
import jakarta.ws.rs.*;
import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.core.Context;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

/**
 * JAX-RS ресурс аутентификации.
 *
 * POST /api/auth/login
 * POST /api/auth/register
 * POST /api/auth/logout
 * POST /api/auth/refresh
 * POST /api/auth/validate
 */
@Path("/api/auth")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class AuthResource {

    private final AuthService authService = new AuthService();

    // ── POST /api/auth/register ───────────────────────────────────────────────

    @POST
    @Path("/register")
    public Response register(RegisterRequest req) {
        if (req == null) {
            return badRequest("Тело запроса обязательно");
        }
        try {
            AuthResponse resp = authService.register(req);
            return Response.status(Response.Status.CREATED).entity(resp).build();
        } catch (IllegalArgumentException e) {
            return badRequest(e.getMessage());
        }
    }

    // ── POST /api/auth/login ──────────────────────────────────────────────────

    @POST
    @Path("/login")
    public Response login(LoginRequest req) {
        if (req == null) {
            return badRequest("Тело запроса обязательно");
        }
        System.out.println("[RESOURCE] login: username='" + req.getUsername() + "' passwordLen=" + (req.getPassword() != null ? req.getPassword().length() : "null"));
        try {
            AuthResponse resp = authService.login(req);
            return Response.ok(resp).build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.UNAUTHORIZED)
                    .entity(new AuthResponse(false, e.getMessage()))
                    .build();
        }
    }

    // ── POST /api/auth/logout ─────────────────────────────────────────────────

    @POST
    @Path("/logout")
    public Response logout(@Context ContainerRequestContext ctx) {
        try {
            Long userId = (Long) ctx.getProperty("userId");
            if (userId != null) {
                authService.logout(userId);
            }
        } catch (Exception ignored) {}
        return Response.ok(new AuthResponse(true, "Выход выполнен")).build();
    }

    // ── POST /api/auth/refresh ────────────────────────────────────────────────

    @POST
    @Path("/refresh")
    public Response refresh(RefreshTokenRequest req) {
        if (req == null || req.getRefreshToken() == null) {
            return badRequest("Refresh токен обязателен");
        }
        try {
            AuthResponse resp = authService.refresh(req.getRefreshToken());
            return Response.ok(resp).build();
        } catch (IllegalArgumentException e) {
            return Response.status(Response.Status.UNAUTHORIZED)
                    .entity(new AuthResponse(false, e.getMessage()))
                    .build();
        }
    }

    // ── POST /api/auth/validate ───────────────────────────────────────────────

    @POST
    @Path("/validate")
    public Response validate(@Context ContainerRequestContext ctx) {
        Long userId = (Long) ctx.getProperty("userId");
        String username = (String) ctx.getProperty("username");
        if (userId == null) {
            return Response.status(Response.Status.UNAUTHORIZED)
                    .entity(new AuthResponse(false, "Токен недействителен"))
                    .build();
        }
        return Response.ok(AuthResponse.builder()
                .success(true)
                .message("Токен действителен")
                .user(new AuthResponse.UserDTO(userId, username, null))
                .build()).build();
    }

    // ── helpers ───────────────────────────────────────────────────────────────

    private Response badRequest(String msg) {
        return Response.status(Response.Status.BAD_REQUEST)
                .entity(new AuthResponse(false, msg))
                .build();
    }
}

