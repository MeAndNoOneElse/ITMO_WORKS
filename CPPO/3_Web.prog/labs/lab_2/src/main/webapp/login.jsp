<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<html>
<head>
    <title>Вход</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="login-form-block">
    <h2>Пожалуйста, войдите</h2>
    <form id="loginForm" method="POST" action="login">
        <input type="hidden" name="action" value="login" />
        <label>
            Введите ваш ID:
            <input type="text" name="userId" required class="login-input" maxlength="10"/>
        </label>
        <button type="submit">Войти</button>
    </form>
</div>
</body>
</html>
