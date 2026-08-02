package com.weblab.filter;

import jakarta.servlet.*;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import java.io.IOException;
@Component
@Order(0)
@Slf4j
public class RequestLoggingFilter implements Filter {

    private static final ThreadLocal<Long> requestStartTime = new ThreadLocal<>();

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {

        if (request instanceof HttpServletRequest) {
            HttpServletRequest httpRequest = (HttpServletRequest) request;

            String method = httpRequest.getMethod();
            String uri = httpRequest.getRequestURI();
            String query = httpRequest.getQueryString();
            String fullUrl = query != null ? uri + "?" + query : uri;

            requestStartTime.set(System.currentTimeMillis());

            log.info("========================================");
            log.info("HTTP REQUEST: {} {}", method, fullUrl);

            try {
                chain.doFilter(request, response);

            } finally {
                Long startTime = requestStartTime.get();
                if (startTime != null) {
                    long executionTime = System.currentTimeMillis() - startTime;

                    log.info("========================================");
                    log.info("HTTP RESPONSE: {} {} | Time: {}ms",
                            method, fullUrl, executionTime);

                    requestStartTime.remove();
                }
            }
        } else {
            chain.doFilter(request, response);
        }
    }
}

