package Filters;

import jakarta.servlet.*;
import jakarta.servlet.annotation.WebFilter;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;

@WebFilter(filterName = "FilterAllowOnlyControllerAndStatic", urlPatterns = {"/*"})
public class FilterOnlyController implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest request = (HttpServletRequest) req;
        HttpServletResponse response = (HttpServletResponse) res;
        String path = request.getServletPath();

        if (path.equals("/controller") ||
                path.equals("/login") ||
                path.endsWith(".jsp") ||
                path.endsWith(".css") ||
                path.endsWith(".js")) {
            chain.doFilter(request, response);
            return;
        }

        // Для всего остального — ошибка
        response.sendError(HttpServletResponse.SC_FORBIDDEN,
                "Доступ разрешён только к /controller, /index.jsp и статическим ресурсам!");
    }
}

