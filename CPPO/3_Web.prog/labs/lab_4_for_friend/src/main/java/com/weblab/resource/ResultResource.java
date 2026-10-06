package com.weblab.resource;

import com.weblab.dto.PointRequest;
import com.weblab.dto.ResultResponse;
import com.weblab.service.ResultService;
import jakarta.ws.rs.*;
import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.core.Context;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.util.List;
import java.util.Map;

/**
 * JAX-RS ресурс результатов (точек).
 *
 * GET    /api/results           — получить все точки пользователя
 * POST   /api/results/check     — добавить и проверить точку
 * DELETE /api/results           — очистить все точки пользователя
 */
@Path("/api/results")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class ResultResource {

    private final ResultService resultService = new ResultService();

    // ── GET /api/results ──────────────────────────────────────────────────────

    @GET
    public Response getAll(@Context ContainerRequestContext ctx) {
        long userId = requireUserId(ctx);
        List<ResultResponse> results = resultService.getAll(userId);
        return Response.ok(results).build();
    }

    // ── POST /api/results/check ───────────────────────────────────────────────

    @POST
    @Path("/check")
    public Response check(PointRequest req, @Context ContainerRequestContext ctx) {
        if (req == null) {
            return badRequest("Тело запроса обязательно");
        }
        long userId = requireUserId(ctx);
        try {
            ResultResponse result = resultService.checkPoint(req, userId);
            return Response.status(Response.Status.CREATED).entity(result).build();
        } catch (IllegalArgumentException e) {
            return badRequest(e.getMessage());
        }
    }

    // ── DELETE /api/results ───────────────────────────────────────────────────

    @DELETE
    public Response clear(@Context ContainerRequestContext ctx) {
        long userId = requireUserId(ctx);
        resultService.clearAll(userId);
        return Response.ok(Map.of("success", true, "message", "Все результаты очищены")).build();
    }

    // ── helpers ───────────────────────────────────────────────────────────────

    private long requireUserId(ContainerRequestContext ctx) {
        Long userId = (Long) ctx.getProperty("userId");
        if (userId == null) throw new NotAuthorizedException("Требуется авторизация");
        return userId;
    }

    private Response badRequest(String msg) {
        return Response.status(Response.Status.BAD_REQUEST)
                .entity(Map.of("success", false, "message", msg))
                .build();
    }
}

