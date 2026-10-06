package Servlets;


import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;


@WebServlet(name = "LogoutServlet", urlPatterns = "/logout")
public class LogoutServlet extends HttpServlet {
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
            throws IOException {
        // Удалить JWT cookie
        Cookie cookie = new Cookie("jwt", "");
        cookie.setMaxAge(0); // немедленно истекает
        cookie.setPath("/");
        resp.addCookie(cookie);

        resp.sendRedirect(req.getContextPath() + "/login.jsp");
    }
}
