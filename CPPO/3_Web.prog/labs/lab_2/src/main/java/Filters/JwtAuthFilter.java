package Filters;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import jakarta.servlet.*;
import jakarta.servlet.annotation.WebFilter;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import javax.crypto.SecretKey;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

@WebFilter(filterName = "JwtAuthFilter", urlPatterns = {"/*"})
public class JwtAuthFilter implements Filter {

    private static final String SECRET = "gT9vKk2fvJ4yYp8zs4vdoREe9TZoXRVZsNfH8FqIp2s";

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest req = (HttpServletRequest) request;
        HttpServletResponse resp = (HttpServletResponse) response;
        String path = req.getServletPath();
        // Не проверяем JWT на страницах:
        if (path.equals("/login") || path.equals("/login.jsp") || path.endsWith(".css")) {
            chain.doFilter(request, response);
            return;
        }
        String jwt = null;
        if (req.getCookies() != null) {
            for (Cookie cookie : req.getCookies()) {
                if ("jwt".equals(cookie.getName())) {
                    jwt = cookie.getValue(); break;
                }
            }
        }
        if (jwt == null) {
            // Если токена нет — вместо 401 делаем редирект на форму авторизации:
            resp.sendRedirect(req.getContextPath() + "/login.jsp");
            return;
        }

        try {
            // Проверяем и парсим JWT
            SecretKey key = Keys.hmacShaKeyFor(SECRET.getBytes(StandardCharsets.UTF_8));

            Claims claims = Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(jwt)
                    .getPayload();

            String userId = claims.getSubject();
            req.setAttribute("userId", userId);

            chain.doFilter(request, response);

        } catch (JwtException e) {
            resp.sendError(HttpServletResponse.SC_UNAUTHORIZED,
                    "Невалидный JWT токен: " + e.getMessage());
        }
    }
}