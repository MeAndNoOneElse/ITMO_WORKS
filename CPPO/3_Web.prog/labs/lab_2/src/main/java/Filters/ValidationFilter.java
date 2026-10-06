package Filters;

import jakarta.servlet.*;
import jakarta.servlet.annotation.WebFilter;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.math.BigDecimal;
import java.util.Enumeration;

@WebFilter(filterName = "ValidationFilter", urlPatterns = {"/controller"})
public class ValidationFilter implements Filter {
    private static final BigDecimal minX = new BigDecimal("-2");
    private static final BigDecimal maxX = new BigDecimal("2");
    private static final BigDecimal minY = new BigDecimal("-3");
    private static final BigDecimal maxY = new BigDecimal("5");
    private static final BigDecimal minR = new BigDecimal("1");
    private static final BigDecimal maxR = new BigDecimal("4");

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest req = (HttpServletRequest) request;
        HttpServletResponse resp = (HttpServletResponse) response;
        String action = req.getParameter("action");
        if (action.equals("check-area")) {
            // Валидация выполняется только для POST на /controller (отсекаем clear)
            if ("POST".equalsIgnoreCase(req.getMethod()) && req.getParameter("clear") == null) {
                String x = req.getParameter("x");
                String y = req.getParameter("y");
                String r = req.getParameter("r");

                // Проверка наличия параметров
                if (x == null || y == null || r == null ||
                        x.trim().isEmpty() || y.trim().isEmpty() || r.trim().isEmpty()) {
                    resp.sendError(HttpServletResponse.SC_BAD_REQUEST,
                            "Отсутствуют обязательные параметры: x, y, r");
                    return;
                }

                // Проверка количества пользовательских параметров
                Enumeration<String> params = req.getParameterNames();
                int count = 0;
                while (params.hasMoreElements()) {
                    String paramName = params.nextElement();
                    if (!"userId".equals(paramName)) { // userId может идти отдельно
                        count++;
                    }
                }
                if (count != 4) {
                    resp.sendError(HttpServletResponse.SC_BAD_REQUEST,
                            "Аргументов должно быть ровно 3: x, y, r");
                    return;
                }

                // Проверка числового формата и диапазонов
                StringBuilder errorMessage = new StringBuilder();
                try {
                    BigDecimal xBD = new BigDecimal(x.trim());
                    BigDecimal yBD = new BigDecimal(y.trim());
                    BigDecimal rBD = new BigDecimal(r.trim());

                    if (xBD.compareTo(minX) < 0 || xBD.compareTo(maxX) > 0)
                        errorMessage.append("X должен быть в диапазоне [-2, 2]. ");
                    if (yBD.compareTo(minY) <= 0 || yBD.compareTo(maxY) >= 0)
                        errorMessage.append("Y должен быть в диапазоне (-3, 5). ");
                    if (rBD.compareTo(minR) < 0 || rBD.compareTo(maxR) > 0)
                        errorMessage.append("R должен быть в диапазоне [1, 4]. ");
                } catch (NumberFormatException e) {
                    resp.sendError(HttpServletResponse.SC_BAD_REQUEST,
                            "Параметры x, y, r должны быть числами");
                    return;
                }

                if (errorMessage.length() > 0) {
                    resp.sendError(HttpServletResponse.SC_BAD_REQUEST, errorMessage.toString().trim());
                    return;
                }
            }
        }
        // Всё ок — пропускаем дальше
        chain.doFilter(request, response);
    }
}