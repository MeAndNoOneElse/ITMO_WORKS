package Servlets;

import jakarta.servlet.ServletContext;
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;
@WebServlet(name = "ControllerServlet", urlPatterns = "/controller")
public class ControllerServlet extends HttpServlet {
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws ServletException, IOException {
        String action = req.getParameter("action");
        if ("check-area".equals(action)) {
            req.getRequestDispatcher("/area-check").forward(req, resp);

        } else if ("clear".equals(action)) {
            req.getRequestDispatcher("/clear").forward(req, resp);

        } else if ("logout".equals(action)) {
            req.getRequestDispatcher("/logout").forward(req, resp);

        } else {
            resp.sendError(HttpServletResponse.SC_BAD_REQUEST, action);

        }
    }
}