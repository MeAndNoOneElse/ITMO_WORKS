package Servlets;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import javax.crypto.SecretKey;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Date;

@WebServlet(name = "LoginServlet", urlPatterns = "/login")
public class LoginServlet extends HttpServlet {

    // Секретный ключ для подписи JWT (минимум 256 бит для HS256)
    private static final String SECRET = "gT9vKk2fvJ4yYp8zs4vdoREe9TZoXRVZsNfH8FqIp2s";

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        resp.setContentType("application/json; charset=UTF-8");

        String userId = req.getParameter("userId");

        if (userId == null || userId.trim().isEmpty()) {
            resp.sendError(HttpServletResponse.SC_BAD_REQUEST, "userId обязателен");
            return;
        }

        try {
            // Генерируем JWT токен
            SecretKey key = Keys.hmacShaKeyFor(SECRET.getBytes(StandardCharsets.UTF_8));

            String jwt = Jwts.builder()
                    .subject(userId)
                    .issuedAt(new Date())
                    .expiration(new Date(System.currentTimeMillis() + 3600000)) // 1 час
                    .signWith(key)
                    .compact();

            // Устанавливаем JWT в httpOnly cookie
            Cookie cookie = new Cookie("jwt", jwt);
            cookie.setHttpOnly(true);  // Защита от XSS
            cookie.setSecure(true);   // Для разработки = false, для продакшена = true (HTTPS)
            cookie.setPath("/");
            cookie.setMaxAge(3600);    // 1 час

            resp.addCookie(cookie);

            // Возвращаем успешный ответ
            resp.sendRedirect(req.getContextPath() + "/index.jsp?auth=ok");


        } catch (Exception e) {
            resp.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR,
                    "Ошибка генерации токена: " + e.getMessage());
        }
    }
}