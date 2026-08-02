<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/fmt" prefix="fmt" %>
<%@ taglib prefix="fn" uri="http://java.sun.com/jsp/jstl/functions" %>
<%@ page import="jakarta.servlet.http.Cookie" %>



<c:set var="userId" value="${requestScope.userId}" />
<c:set var="userResults" value="${applicationScope.resultsMap[userId]}" />
<c:set var="currentR" value="${applicationScope.currentRMap[userId]}" />

<!DOCTYPE html>
<html>
<head>
    <title>Проверка попадания точки</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
<%
    String userId = (String) request.getAttribute("userId");
    boolean isAuthenticated = (userId != null );

%>

<% if (isAuthenticated) { %>
<div id = "authoris" >
    <span>Вы авторизовались по id = <%= userId %></span>
    <form method="POST" action="controller" >
        <input type="hidden" name="action" value="logout" />
        <button type="submit">Выйти</button>
    </form>
</div>
<%}%>
<br>

<script>
    window.userResults = [
        <c:forEach var="row" items="${userResults}" varStatus="status">
        {
            x: ${row.x},
            y: ${row.y},
            r: ${row.r},
            hit: ${row.hit}
        }<c:if test="${!status.last}">,</c:if>
        </c:forEach>
    ];
</script>
<div class="start">
    <div id="name">
        <h1>Лабораторная №2</h1>
        <h2>Проверка попадания точки на координатной плоскости</h2>
    </div>
    <div id="info">
        <p><strong>ФИО:</strong> Ануфриев Андрей Сергеевич</p>
        <p><strong>Группа:</strong> P3219</p>
        <p><strong>Вариант:</strong> 8484</p>
    </div>
</div>
<br>
<div class="main">
    <div id="form">
        <form id="checkForm" action="controller" method="post">
            <input type="hidden" name="action" value="check-area" />
            <fieldset>
                <legend>Координаты точки</legend>
                <div>
                    <span>X:</span>
                    <!-- X выбирается радиокнопками -->
                    <div class="radio-table">
                        <c:forEach var="vx" items="${fn:split('-2,-1.5,-1,-0.5,0,0.5,1,1.5,2', ',')}">
                            <input type="radio" name="x" value="${vx}" id="x_${vx}" required>
                            <label for="x_${vx}">${vx}</label>
                        </c:forEach>
                    </div>
                </div>
                <div>
                    <label for="y">Y:</label>
                    <input type="text" name="y" id="y" maxlength="10" required placeholder="от -3 до 5"
                           inputmode="decimal">
                </div>
                <div>
                    <label for="r">R:</label>
                    <input type="text" name="r" id="r" maxlength="10" required placeholder="от 1 до 4"
                           value="${currentR != null ? currentR : ''}" inputmode="decimal">
                </div>
                <input type="hidden" name="userId" id="userIdField" />
                <button type="submit">Проверить</button>
                <div>Последний выбранный R: <b>${currentR}</b></div>
            </fieldset>
        </form>
    </div>
    <div id="graph">
        <canvas id="coordinatePlane" width="400" height="400"></canvas>
        <script>
            window.currentR = ${applicationScope .currentR != null ? applicationScope .currentR : 2};
        </script>
    </div>
</div>


<!-- Место для сообщения/ошибки -->
<div id="modal" class="modal-background hidden">
    <div class="modal-window">
        <span id="modalMsg"></span>
        <button id="modalCancelBtn">Отмена</button>
        <button id="modalBtn">ОК</button>

    </div>
</div>

<br>
<div id="end">
    <h3 class="table-title">История проверок</h3>
    <c:set var="userResults" value="${applicationScope.resultsMap[userId]}" />
    <div id="table">
        <c:choose>
            <c:when test="${empty userResults}">
                <p>Пока нет результатов. Проверьте хотя бы одну точку.</p>
            </c:when>
            <c:otherwise>
                <table>
                    <tr>
                        <th>X</th>
                        <th>Y</th>
                        <th>R</th>
                        <th>Результат</th>
                        <th>Время</th>
                        <th>Время выполнения</th>
                    </tr>
                    <c:forEach var="row" items="${userResults}">
                        <tr class="${row.hit ? 'hit' : 'miss'}">
                            <td>${row.x}</td>
                            <td>${row.y}</td>
                            <td>${row.r}</td>
                            <td>
                                    ${row.hit ? 'Попало' : 'Не попало'}
                            </td>
                            <td><fmt:formatDate value="${row.timestamp}" pattern="HH:mm:ss"/></td>
                            <td><fmt:formatNumber value="${row.executionTimeMillis}" pattern="0.000"/> мс</td>
                        </tr>
                    </c:forEach>
                </table>
            </c:otherwise>
        </c:choose>
    </div>
</div>
<script src="script.js"></script>
<script src="canvas.js"></script>
<script>
    window.onload = function () {
        const points = [];
        <c:forEach var="row" items="${applicationScope .results}">
        points.push({x: ${row.x}, y: ${row.y}, hit: ${row.hit}, r: ${row.r}});
        </c:forEach>
        if (window.drawResultHistory) window.drawResultHistory(points);
    };
</script>
<form id="clearForm" action="controller" method="post" style="display:none">
    <input type="hidden" name="action" value="clear" />
    <input type="hidden" name="clear" value="true">
    <input type="hidden" name="userId" id="clearUserId">
</form>
<button id="clearResultsBtn" type="button">Очистить историю</button>
<%--<input type="hidden" name="userId" id="userIdField">--%>

</body>
</html>
