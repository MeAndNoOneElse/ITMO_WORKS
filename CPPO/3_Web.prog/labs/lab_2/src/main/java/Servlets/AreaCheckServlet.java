package Servlets;

import Untils.ResultRow;
import jakarta.servlet.ServletContext;
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.math.BigDecimal;
import java.util.*;

@WebServlet(name = "AreaCheckServlet", urlPatterns = "/area-check")
public class AreaCheckServlet extends HttpServlet {

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {

        resp.setContentType("text/html; charset=UTF-8");
        long startTime = System.nanoTime();

        try {
            // Получаем userId из атрибута запроса (установлен JwtAuthFilter)
            String userId = (String) req.getAttribute("userId");

            double x = new BigDecimal(req.getParameter("x").trim()).doubleValue();
            double y = new BigDecimal(req.getParameter("y").trim()).doubleValue();
            double r = new BigDecimal(req.getParameter("r").trim()).doubleValue();

            boolean isHit = checkHit(x, y, r);

            long endTime = System.nanoTime();
            long executionTime = endTime - startTime;

            ServletContext context = getServletContext();

            synchronized (context) {
                Map<String, List<ResultRow>> resultsMap =
                        (Map<String, List<ResultRow>>) context.getAttribute("resultsMap");

                if (resultsMap == null) {
                    resultsMap = new HashMap<>();
                    context.setAttribute("resultsMap", resultsMap);
                }

                List<ResultRow> results = resultsMap.get(userId);
                if (results == null) {
                    results = new ArrayList<>();
                    resultsMap.put(userId, results);
                }

                Date now = new Date();
                results.add(new ResultRow(x, y, r, isHit, now, executionTime));
                context.setAttribute("resultsMap", resultsMap);

                Map<String, Double> currentRMap =
                        (Map<String, Double>) context.getAttribute("currentRMap");

                if (currentRMap == null) {
                    currentRMap = new HashMap<>();
                    context.setAttribute("currentRMap", currentRMap);
                }

                currentRMap.put(userId, r);
                context.setAttribute("currentRMap", currentRMap);
            }

            resp.sendRedirect(req.getContextPath() + "/index.jsp");

        } catch (Exception e) {
            resp.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR,
                    "Ошибка обработки запроса: " + e.getMessage());
        }
    }

    private boolean checkHit(double x, double y, double r) {
        boolean inTriangle = (-r / 2 <= x && x <= 0 && 0 <= y && y <= r && y <= 2 * x + r);
        boolean inRectangle = (x >= 0 && x <= r && y <= 0 && y >= -r / 2);
        boolean inCircle = (x <= 0 && y <= 0 && (x * x + y * y) <= r * r);
        return inTriangle || inRectangle || inCircle;
    }
}