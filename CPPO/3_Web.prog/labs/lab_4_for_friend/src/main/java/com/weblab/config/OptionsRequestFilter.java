package com.weblab.config;

import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.container.ContainerRequestFilter;
import jakarta.ws.rs.container.PreMatching;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.Provider;
import java.io.IOException;

/**
 * Обработчик preflight OPTIONS-запросов для CORS.
 */
@Provider
@PreMatching
public class OptionsRequestFilter implements ContainerRequestFilter {

    @Override
    public void filter(ContainerRequestContext ctx) throws IOException {
        if ("OPTIONS".equalsIgnoreCase(ctx.getMethod())) {
            ctx.abortWith(Response.ok()
                    .header("Access-Control-Allow-Origin", "*")
                    .header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
                    .header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Forwarded-For, User-Agent")
                    .header("Access-Control-Max-Age", "86400")
                    .build());
        }
    }
}

