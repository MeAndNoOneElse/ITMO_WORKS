package com.weblab.config;

import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.container.ContainerResponseContext;
import jakarta.ws.rs.container.ContainerResponseFilter;
import jakarta.ws.rs.ext.Provider;
import java.io.IOException;

/**
 * CORS-фильтр — разрешает запросы от Vue-фронтенда.
 */
@Provider
public class CorsFilter implements ContainerResponseFilter {

    @Override
    public void filter(ContainerRequestContext req, ContainerResponseContext resp) throws IOException {
        resp.getHeaders().add("Access-Control-Allow-Origin", "*");
        resp.getHeaders().add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
        resp.getHeaders().add("Access-Control-Allow-Headers",
                "Content-Type, Authorization, X-Forwarded-For, User-Agent");
        resp.getHeaders().add("Access-Control-Max-Age", "86400");
    }
}

