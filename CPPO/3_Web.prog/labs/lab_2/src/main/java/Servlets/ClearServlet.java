package Servlets;

import Untils.ResultRow;
import jakarta.servlet.ServletContext;
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.util.List;
import java.util.Map;

@WebServlet(name = "ClearServlet", urlPatterns = "/clear")
public class ClearServlet extends HttpServlet {

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        resp.setContentType("text/html; charset=UTF-8");

        // Получаем userId из атрибута запроса (установлен JwtAuthFilter)
        String userId = (String) req.getAttribute("userId");

        if (userId != null && !userId.isEmpty()) {
            ServletContext context = getServletContext();

            // Удаляем историю результатов для этого пользователя
            Map<String, List<ResultRow>> resultsMap =
                    (Map<String, List<ResultRow>>) context.getAttribute("resultsMap");

            if (resultsMap != null) {
                resultsMap.remove(userId);
                context.setAttribute("resultsMap", resultsMap);
            }

            // Удаляем текущий R для этого пользователя
            Map<String, Double> currentRMap =
                    (Map<String, Double>) context.getAttribute("currentRMap");

            if (currentRMap != null) {
                currentRMap.remove(userId);
                context.setAttribute("currentRMap", currentRMap);
            }
        }

        resp.sendRedirect("index.jsp");
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        resp.sendError(HttpServletResponse.SC_METHOD_NOT_ALLOWED,
                "Метод GET не поддерживается для очистки. Используйте POST");
    }
}