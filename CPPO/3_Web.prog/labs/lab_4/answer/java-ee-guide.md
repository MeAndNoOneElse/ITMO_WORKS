# Полный разбор Java EE, Spring, React и Angular

## 1. Java EE: Спецификации и реализации

### Что такое Java EE?

**Java EE (Enterprise Edition)** — это набор спецификаций и стандартов для разработки масштабируемых, надежных, распределенных корпоративных приложений. Важный момент: Java EE содержит не реализацию, а только **спецификацию** (описание того, как должна работать технология).

**Ключевые характеристики:**

-   Спецификация, а не конкретная реализация
-   Определяет интерфейсы, классы и обязательное поведение
-   Реализуется разными поставщиками (Oracle GlassFish, Red Hat JBoss, Apache TomEE, Payara)
-   Обновления: Java EE → Jakarta EE (с версии 8, 2019 год)

### Спецификации в Java EE

**Основные спецификации:**

1.  **Servlet (Java Servlet Specification)**
    
    -   Базовая технология для обработки HTTP-запросов
    -   Определяет жизненный цикл сервлетов
    -   Позволяет создавать веб-приложения
2.  **JSP (JavaServer Pages)**
    
    -   Спецификация для создания динамических веб-страниц
    -   Предоставляет шаблонизацию на серверной стороне
    -   Компилируется в сервлеты
3.  **CDI (Contexts and Dependency Injection)**
    
    -   Управление жизненным циклом компонентов
    -   Dependency Injection (внедрение зависимостей)
    -   Позволяет создавать слабо связанные компоненты
4.  **EJB (Enterprise JavaBeans)**
    
    -   Компоненты бизнес-логики
    -   Session Beans, Message-Driven Beans, Entity Beans
    -   Поддерживает транзакции, безопасность, масштабируемость
5.  **JPA (Java Persistence API)**
    
    -   Спецификация для работы с базами данных
    -   ORM (Object-Relational Mapping)
    -   Определяет аннотации @Entity, @Column и т.д.
6.  **JAX-RS (Java API for RESTful Web Services)**
    
    -   Создание REST веб-сервисов
    -   Аннотации @Path, @GET, @POST и т.д.
7.  **JAX-WS (Java API for XML Web Services)**
    
    -   Создание SOAP веб-сервисов
    -   Работа с XML
8.  **JMS (Java Message Service)**
    
    -   Асинхронная передача сообщений
    -   Очереди сообщений
9.  **JTA (Java Transaction API)**
    
    -   Управление транзакциями
    -   Поддержка ACID свойств
10.  **JavaMail**
     
     -   Отправка электронной почты
     -   Работа с SMTP, POP3, IMAP

### Реализации Java EE

Реализация

Разработчик

Особенности

**GlassFish**

Oracle

Эталонная реализация, полная поддержка спецификации

**WildFly**

Red Hat

Легкий, быстрый, хорошо документирован

**TomEE**

Apache

Компактная реализация, встроена в Tomcat

**Payara**

Payara Services

Форк GlassFish, оптимизирован для микросервисов

**IBM WebSphere**

IBM

Корпоративное решение с расширенными возможностями

---

## 2. Принципы IoC, CDI и Location Transparency

### Inversion of Control (IoC)

**IoC (Инверсия управления)** — принцип, при котором контроль над созданием объектов и управлением их жизненным циклом передается **контейнеру**, а не приложению.

**Традиционный подход (без IoC):**

```java
// Приложение сами создает зависимости
public class OrderService {
    private UserRepository userRepository;
    private OrderRepository orderRepository;
    
    public OrderService() {
        this.userRepository = new UserRepository();  // Прямое создание
        this.orderRepository = new OrderRepository(); // Прямое создание
    }
}
```

**Проблемы:**

-   Жесткая связанность (tight coupling)
-   Сложно тестировать (нельзя подменить реализацию)
-   Трудно менять реализации

**С IoC контейнером:**

```java
// Контейнер создает и внедряет зависимости
public class OrderService {
    private UserRepository userRepository;
    private OrderRepository orderRepository;
    
    @Inject  // CDI контейнер внедрит зависимость
    public OrderService(UserRepository userRepository, 
                       OrderRepository orderRepository) {
        this.userRepository = userRepository;
        this.orderRepository = orderRepository;
    }
}
```

**Преимущества:**

-   Слабая связанность (loose coupling)
-   Легче тестировать
-   Можно быстро менять реализации
-   Контейнер управляет жизненным циклом

### CDI (Contexts and Dependency Injection)

**CDI** — это стандартная спецификация Java EE для внедрения зависимостей и управления жизненным циклом компонентов.

**Основные концепции CDI:**

1.  **Beans (Бины)**
    
    -   Объекты, управляемые CDI контейнером
    -   Могут иметь разные области видимости (scope)
    -   Должны быть обнаружены контейнером
2.  **Dependency Injection**
    
    ```java
    @Inject  // Внедрение зависимости
    private UserRepository userRepository;
    ```
    
3.  **Scopes (Области видимости)**
    
    -   **@Dependent** — зависимый объект (создается и уничтожается вместе с потребителем)
    -   **@RequestScoped** — на каждый HTTP запрос новый объект
    -   **@SessionScoped** — один объект на HTTP сессию
    -   **@ApplicationScoped** — один объект на все приложение
    -   **@ConversationScoped** — на протяжении многошагового диалога
4.  **Qualifiers (Квалификаторы)**
    
    -   Помогают различать разные реализации интерфейса
    
    ```java
    @Qualifier
    @Retention(RUNTIME)
    @Target({FIELD, PARAMETER})
    public @interface Async { }
    
    // Использование
    @Inject @Async
    private MessageService messageService;
    ```
    
5.  **Producers (Производители)**
    
    -   Методы для создания сложных объектов
    
    ```java
    @Produces
    public DataSource getDataSource() {
        return createDataSource("jdbc:mysql://localhost/db");
    }
    ```
    
6.  **Events (События)**
    
    -   Слабо связанная коммуникация между компонентами
    
    ```java
    @Inject
    private Event<UserCreatedEvent> userCreatedEvent;
    
    userCreatedEvent.fire(new UserCreatedEvent(user));
    ```
    

### Location Transparency

**Location Transparency** — принцип, при котором клиент не знает, где физически находится объект или сервис (локально или удаленно).

**Пример в Java EE:**

```java
// Клиент вызывает сервис одинаково, независимо от его расположения
@Inject
private OrderService orderService;  // Может быть локальным или удаленным

orderService.createOrder(order);  // Один и тот же вызов
```

**В EJB это реализуется через:**

-   **Local interface** — для локального вызова
-   **Remote interface** — для удаленного вызова
-   **WebService** — через REST/SOAP

Контейнер автоматически заботится о сетевом взаимодействии, маршализации объектов и обработке ошибок.

---

## 3. Компоненты и контейнеры

### Что такое контейнер?

**Контейнер** — это среда выполнения, которая управляет:

-   Созданием объектов (instantiation)
-   Внедрением зависимостей (injection)
-   Жизненным циклом компонентов
-   Конфигурацией
-   Безопасностью
-   Транзакциями
-   Масштабируемостью

**Процесс работы контейнера:**

```
1. BOOTSTRAP
   ↓ Контейнер инициализируется
   
2. DISCOVERY
   ↓ Сканируются классы с аннотациями (@WebServlet, @Stateless, @Entity)
   
3. PROCESSING
   ↓ Обработка аннотаций и конфигурации
   
4. PROVISIONING
   ↓ Создание объектов, внедрение зависимостей
   
5. RUNTIME
   ↓ Контейнер управляет объектами во время выполнения
```

### Типы компонентов

**1. Managed Beans**

-   Простые объекты, управляемые CDI
-   Обнаруживаются по наличию аннотаций или конфигурации
-   Могут иметь разные scope

```java
@ApplicationScoped  // Один объект на приложение
public class ConfigManager {
    private Properties config;
    
    @PostConstruct
    public void init() {
        config = loadConfig();
    }
}
```

**2. Enterprise JavaBeans (EJB)**

-   Компоненты бизнес-логики
-   Поддерживают транзакции и безопасность
-   Могут быть Session, Message-Driven, Entity

**3. Web Components**

-   Сервлеты (Servlet)
-   Фильтры (Filter)
-   Слушатели (Listener)

**4. Resource Adapters**

-   Адаптеры для подключения к внешним системам
-   Поддерживают JCA (Java Connector Architecture)

### Жизненный цикл компонента

**Управляемый бин (Managed Bean):**

```
1. CONSTRUCTION
   ↓ Контейнер вызывает конструктор

2. INJECTION
   ↓ Внедряются зависимости (@Inject)

3. POST_CONSTRUCT
   ↓ Вызывается метод с аннотацией @PostConstruct
   
4. ACTIVE
   ↓ Бин готов к использованию
   ↓ Может быть использован многими клиентами (зависит от scope)
   
5. PRE_DESTROY
   ↓ Вызывается метод с аннотацией @PreDestroy
   ↓ Вводится при выходе из области видимости
   
6. DESTRUCTION
   ↓ Объект удаляется
```

**Пример:**

```java
@RequestScoped
public class UserValidator {
    @Inject
    private UserRepository userRepository;
    
    @PostConstruct
    public void init() {
        System.out.println("Инициализация валидатора");
        // Инициализация ресурсов
    }
    
    public void validate(User user) {
        // Валидация пользователя
    }
    
    @PreDestroy
    public void cleanup() {
        System.out.println("Очистка валидатора");
        // Освобождение ресурсов
    }
}
```

---

## 4. Дескрипторы развертывания

**Дескриптор развертывания (Deployment Descriptor)** — это XML-файл, который описывает конфигурацию приложения для контейнера.

### Основные дескрипторы

**1. web.xml (Web Application Deployment Descriptor)**

Расположение: `WEB-INF/web.xml`

Назначение: Конфигурация веб-приложения

```xml
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee 
         http://xmlns.jcp.org/xml/ns/javaee/web-app_4_0.xsd"
         version="4.0">
    
    <!-- Описание приложения -->
    <display-name>My Web Application</display-name>
    <description>Sample web application</description>
    
    <!-- Объявление сервлета -->
    <servlet>
        <servlet-name>userServlet</servlet-name>
        <servlet-class>com.example.UserServlet</servlet-class>
    </servlet>
    
    <!-- Маппинг URL на сервлет -->
    <servlet-mapping>
        <servlet-name>userServlet</servlet-name>
        <url-pattern>/users/*</url-pattern>
    </servlet-mapping>
    
    <!-- Фильтр -->
    <filter>
        <filter-name>logFilter</filter-name>
        <filter-class>com.example.LogFilter</filter-class>
    </filter>
    
    <filter-mapping>
        <filter-name>logFilter</filter-name>
        <url-pattern>/*</url-pattern>
    </filter-mapping>
    
    <!-- Параметры контекста приложения -->
    <context-param>
        <param-name>database.url</param-name>
        <param-value>jdbc:mysql://localhost/mydb</param-value>
    </context-param>
    
    <!-- Слушатель событий -->
    <listener>
        <listener-class>com.example.ApplicationListener</listener-class>
    </listener>
    
    <!-- Сессия -->
    <session-config>
        <cookie-config>
            <http-only>true</http-only>
            <secure>true</secure>
        </cookie-config>
        <tracking-mode>COOKIE</tracking-mode>
        <timeout>30</timeout>
    </session-config>
    
    <!-- Обработка ошибок -->
    <error-page>
        <error-code>404</error-code>
        <location>/error/404.jsp</location>
    </error-page>
    
    <!-- Welcome файлы -->
    <welcome-file-list>
        <welcome-file>index.html</welcome-file>
        <welcome-file>index.jsp</welcome-file>
    </welcome-file-list>
</web-app>
```

**2. ejb-jar.xml (EJB Deployment Descriptor)**

Расположение: `META-INF/ejb-jar.xml`

Назначение: Конфигурация EJB компонентов

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ejb-jar xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee 
         http://xmlns.jcp.org/xml/ns/javaee/ejb-jar_3_2.xsd"
         version="3.2">
    
    <display-name>My EJB Module</display-name>
    
    <!-- Объявление Session Bean -->
    <enterprise-beans>
        <session>
            <ejb-name>OrderService</ejb-name>
            <ejb-class>com.example.OrderServiceBean</ejb-class>
            <session-type>Stateless</session-type>
            
            <!-- Локальный интерфейс -->
            <local>com.example.OrderService</local>
            
            <!-- Удаленный интерфейс -->
            <remote>com.example.OrderServiceRemote</remote>
            
            <!-- Конфигурация транзакций -->
            <transaction-type>Container</transaction-type>
        </session>
    </enterprise-beans>
    
    <!-- Сборщик методов -->
    <assembly-descriptor>
        <container-transaction>
            <method>
                <ejb-name>OrderService</ejb-name>
                <method-name>*</method-name>
            </method>
            <trans-attribute>Required</trans-attribute>
        </container-transaction>
    </assembly-descriptor>
</ejb-jar>
```

**3. beans.xml (CDI Configuration)**

Расположение: `WEB-INF/beans.xml` или `META-INF/beans.xml`

Назначение: Активация CDI в приложении

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://xmlns.jcp.org/xml/ns/javaee"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee 
       http://xmlns.jcp.org/xml/ns/javaee/beans_2_0.xsd"
       bean-discovery-mode="all">
    
    <!-- Альтернативные реализации -->
    <alternatives>
        <class>com.example.MockOrderRepository</class>
    </alternatives>
    
    <!-- Interceptors -->
    <interceptors>
        <class>com.example.LoggingInterceptor</class>
    </interceptors>
    
    <!-- Decorators -->
    <decorators>
        <class>com.example.CachedOrderDecorator</class>
    </decorators>
</beans>
```

### Современный подход: Аннотации вместо XML

С Java EE 6+ большинство конфигураций можно заменить аннотациями:

```java
// Вместо объявления в web.xml
@WebServlet("/users/*")
public class UserServlet extends HttpServlet {
    // ...
}

// Вместо объявления фильтра в web.xml
@WebFilter("/*")
public class LogFilter implements Filter {
    // ...
}

// Вместо объявления слушателя в web.xml
@WebListener
public class ApplicationListener implements ServletContextListener {
    // ...
}
```

---

## 5. Java EE API

### Основные API

**1. Servlet API**

-   Обработка HTTP запросов и ответов
-   `HttpServlet`, `HttpServletRequest`, `HttpServletResponse`

**2. JSP API**

-   Создание динамических веб-страниц
-   `PageContext`, `JspWriter`

**3. CDI API**

-   Внедрение зависимостей и управление жизненным циклом
-   `@Inject`, `@Produces`, `Instance<T>`

**4. EJB API**

-   Компоненты бизнес-логики
-   `@Stateless`, `@Stateful`, `@MessageDriven`

**5. JPA API**

-   Работа с базами данных через ORM
-   `EntityManager`, `@Entity`, `@Column`

**6. JAX-RS API**

-   Создание REST веб-сервисов
-   `@Path`, `@GET`, `@POST`, `@RestClient`

**7. JAX-WS API**

-   Создание SOAP веб-сервисов
-   `@WebService`, `@WebMethod`

**8. JMS API**

-   Асинхронная передача сообщений
-   `Connection`, `Session`, `MessageProducer`, `MessageConsumer`

**9. JTA API**

-   Управление транзакциями
-   `UserTransaction`, `@Transactional`

**10. JavaMail API**

-   Отправка электронной почты
-   `Session`, `Message`, `Transport`

**11. JCA API (Java Connector Architecture)**

-   Подключение к внешним системам
-   Resource Adapters

---

## 6. Виды компонентов в Java EE

### 1. Web Components

**Сервлеты (Servlet)**

-   Основа веб-приложений
-   Обрабатывают HTTP запросы
-   Запускаются в контексте веб-контейнера

```java
@WebServlet("/api/users")
@RequestScoped  // CDI scope
public class UserServlet extends HttpServlet {
    @Inject
    private UserService userService;
    
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) 
            throws ServletException, IOException {
        // Обработка GET запроса
    }
    
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) 
            throws ServletException, IOException {
        // Обработка POST запроса
    }
}
```

**Фильтры (Filter)**

-   Перехватывают запросы и ответы
-   Используются для логирования, аутентификации, сжатия

```java
@WebFilter("/*")
public class LogFilter implements Filter {
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, 
                        FilterChain chain) throws IOException, ServletException {
        System.out.println("Before: " + ((HttpServletRequest)request).getRequestURI());
        chain.doFilter(request, response);
        System.out.println("After");
    }
}
```

**Слушатели (Listener)**

-   Реагируют на события в приложении
-   Инициализируют ресурсы при запуске

```java
@WebListener
public class ApplicationListener implements ServletContextListener {
    @Override
    public void contextInitialized(ServletContextEvent event) {
        System.out.println("Application started");
    }
    
    @Override
    public void contextDestroyed(ServletContextEvent event) {
        System.out.println("Application stopped");
    }
}
```

### 2. Business Logic Components (EJB)

**Session Beans**

-   Выполняют бизнес-логику
-   Управляются контейнером
-   Поддерживают транзакции

**Message-Driven Beans**

-   Обрабатывают сообщения из очередей
-   Асинхронная обработка

### 3. Data Components

**Entity Beans (JPA)**

-   Представляют данные в базе
-   Маршалируются в таблицы
-   Управляются EntityManager

**Managed Beans**

-   CDI компоненты
-   Могут иметь разные scope

---

## 7. Профили платформы Java EE

Java EE предоставляет несколько **профилей** для разных типов приложений:

### 1. Web Profile

**Предназначение:** Веб-приложения

**Включает API:**

-   Servlet
-   JSP
-   EL (Expression Language)
-   JSTL (JavaServer Pages Standard Tag Library)
-   CDI
-   JPA
-   JTA
-   JAX-RS (в некоторых версиях)
-   Validation

**Когда использовать:** Типовые веб-приложения, сайты, простые API

**Пример использования:**

```java
// Web Profile достаточно для этого
@WebServlet("/users")
public class UserServlet extends HttpServlet {
    @Inject
    private UserRepository userRepository;
    // ...
}
```

### 2. Full Profile

**Предназначение:** Полнофункциональные корпоративные приложения

**Включает ВСЕ API:**

-   Все из Web Profile
-   EJB (полная версия)
-   JMS
-   Connector Architecture (JCA)
-   CORBA
-   JavaMail
-   Web Services (JAX-WS)
-   Messaging

**Когда использовать:**

-   Высоконагруженные системы
-   Системы с очередями сообщений
-   Требуется удаленный доступ к EJB
-   Интеграция с другими системами

**Пример использования:**

```java
// Full Profile нужен для Message-Driven Bean
@MessageDriven(activationConfig = {
    @ActivationConfigProperty(propertyName = "destinationType", 
                             propertyValue = "javax.jms.Queue"),
    @ActivationConfigProperty(propertyName = "destination", 
                             propertyValue = "jms/OrderQueue")
})
public class OrderProcessingBean implements MessageListener {
    @Override
    public void onMessage(Message message) {
        // Асинхронная обработка заказа
    }
}
```

### 3. Core Profile (Jakarta EE 9+)

**Предназначение:** Микросервисы, облачные приложения

**Включает API:**

-   CDI (облегченная версия)
-   REST (Jakarta REST)
-   JSON-P, JSON-B

**Когда использовать:**

-   Контейнеризированные приложения
-   Микросервисная архитектура
-   Облачные платформы (Kubernetes)

---

## 8. EJB (Enterprise JavaBeans)

### Что такое EJB?

**EJB (Enterprise JavaBeans)** — это компоненты для реализации бизнес-логики в корпоративных приложениях.

**Характеристики EJB:**

-   Управляются контейнером
-   Поддерживают транзакции, безопасность, масштабируемость
-   Могут быть локальными или удаленными
-   Живут в EJB контейнере

### Типы EJB

**1. Session Beans**

-   Выполняют бизнес-операции
-   Не связаны с данными в БД
-   Создаются клиентом, уничтожаются при завершении сессии

**2. Message-Driven Beans**

-   Обрабатывают асинхронные сообщения
-   Слушают JMS очереди/топики

**3. Entity Beans (устарели)**

-   Представляли данные в БД
-   Заменены на JPA

### Жизненный цикл Session Bean

```
CREATION
  ↓ @PostConstruct
READY
  ↓ Использование (доступны все методы)
  ↓ @PreDestroy
REMOVAL
```

---

## 9. Stateless & Stateful Session Beans

### Stateless Session Bean

**Характеристики:**

-   Не сохраняет состояние между вызовами
-   Может использоваться несколькими клиентами
-   Более производительный (можно переиспользовать экземпляры)
-   Контейнер может создать пул экземпляров

**Пример:**

```java
@Stateless  // Объявление Stateless Bean
public class CalculatorBean {
    // Не содержит состояния, привязанного к клиенту
    
    public int add(int a, int b) {
        return a + b;  // Каждый вызов независим
    }
    
    public int multiply(int a, int b) {
        return a * b;
    }
}
```

**Использование:**

```java
@Inject
private CalculatorBean calculator;

// Каждый вызов может быть обработан разным экземпляром
int result1 = calculator.add(5, 3);
int result2 = calculator.multiply(4, 2);
```

**Преимущества:**

-   Высокая производительность
-   Контейнер может эффективнее управлять ресурсами
-   Лучше масштабируется
-   Нет привязки к клиенту

**Когда использовать:**

-   Вычисления, которые не зависят от состояния
-   Операции с БД (SELECT, INSERT, UPDATE)
-   Бизнес-операции, которые можно выполнить за один вызов

### Stateful Session Bean

**Характеристики:**

-   Сохраняет состояние между вызовами
-   Привязан к конкретному клиенту
-   Контейнер поддерживает отдельный экземпляр для каждого клиента
-   Медленнее, чем Stateless

**Пример:**

```java
@Stateful  // Объявление Stateful Bean
@RequestScoped  // Или @SessionScoped
public class ShoppingCartBean {
    private List<Item> items = new ArrayList<>();
    private double total = 0;
    
    public void addItem(Item item) {
        items.add(item);
        total += item.getPrice();
    }
    
    public void removeItem(Item item) {
        items.remove(item);
        total -= item.getPrice();
    }
    
    public List<Item> getItems() {
        return new ArrayList<>(items);  // Состояние сохраняется!
    }
    
    public double getTotal() {
        return total;  // Состояние сохраняется!
    }
    
    @Remove  // Метод для удаления Bean
    public void checkout() {
        System.out.println("Order placed for total: " + total);
        items.clear();
        total = 0;
    }
}
```

**Использование:**

```java
@Inject
private ShoppingCartBean cart;

// Состояние сохраняется между вызовами!
cart.addItem(new Item("Laptop", 1000));
cart.addItem(new Item("Mouse", 50));

System.out.println(cart.getItems());  // 2 items
System.out.println(cart.getTotal());  // 1050

cart.checkout();  // @Remove удаляет Bean
```

**Процесс жизненного цикла:**

```
1. CREATION
   ↓ Контейнер создает экземпляр для клиента
   
2. POST_CONSTRUCT
   ↓ @PostConstruct инициализирует Bean
   
3. ACTIVE
   ↓ Клиент вызывает методы
   ↓ Состояние сохраняется между вызовами
   ↓ Контейнер может паузировать (passivate) Bean при неиспользовании
   ↓ Контейнер может восстановить (activate) Bean, когда нужен
   
4. PRE_DESTROY
   ↓ @PreDestroy очищает ресурсы
   
5. REMOVAL
   ↓ @Remove удаляет Bean
   ↓ Или контейнер удаляет при timeout
```

**Passivation и Activation:**

При нехватке памяти контейнер может сохранить состояние Stateful Bean на диск (serialization):

```java
@Stateful
public class OrderBean implements Serializable {
    private String orderId;
    private List<Item> items;  // Должны быть сериализуемые
    
    @PostActivate
    public void onActivate() {
        System.out.println("Bean восстановлен из памяти");
    }
    
    @PrePassivate
    public void onPassivate() {
        System.out.println("Bean сохранен на диск");
    }
}
```

**Преимущества Stateful:**

-   Натуральный способ моделирования сессии пользователя
-   Удобно для многошаговых процессов
-   Хорошо подходит для интерактивных приложений

**Недостатки:**

-   Выше затраты памяти
-   Сложнее масштабировать (нельзя просто добавить сервер)
-   Медленнее, чем Stateless
-   Требует сериализации при passivation

**Когда использовать:**

-   Шопинг-корзина
-   Многошаговый процесс регистрации
-   Форма с сохранением данных между шагами
-   Временные данные, привязанные к пользователю

### Сравнение Stateless vs Stateful

Характеристика

Stateless

Stateful

**Состояние**

Не сохраняет

Сохраняет между вызовами

**Привязка к клиенту**

Нет

Да, один экземпляр на клиента

**Производительность**

Высокая

Средняя/низкая

**Масштабируемость**

Отличная

Средняя

**Использование памяти**

Низкое

Высокое

**Когда использовать**

Расчеты, CRUD

Сессионные данные

---

## 10. EJB Lite и EJB Full

### EJB Lite

**Что это?**

-   Облегченная версия EJB, включенная в Web Profile
-   Упрощенное подмножество полного EJB

**Возможности EJB Lite:**

```java
// Stateless Session Beans ✓
@Stateless
public class UserService {
    public User findUser(Long id) { }
}

// Stateful Session Beans ✓
@Stateful
public class ShoppingCart {
    public void addItem(Item item) { }
}

// Локальные интерфейсы ✓
public interface OrderServiceLocal {
    void createOrder(Order order);
}

// Lifecycle callbacks ✓
@PostConstruct
@PreDestroy

// Dependency Injection ✓
@Inject
private UserRepository userRepository;

// Transactions ✓
@Transactional
public void updateUser(User user) { }

// Security ✓
@RolesAllowed("ADMIN")
public void deleteUser(Long id) { }
```

**Ограничения EJB Lite:**

```java
// ✗ Асинхронные методы
@Asynchronous
public void processOrder(Order order) { }

// ✗ Message-Driven Beans
@MessageDriven
public class OrderProcessor implements MessageListener { }

// ✗ Удаленные интерфейсы (Remote)
@Remote
public interface RemoteService { }

// ✗ Timer Service
@Timeout
public void scheduleTask() { }

// ✗ WebService endpoints
@WebService
public class OrderWebService { }
```

### EJB Full

**Что это?**

-   Полная версия EJB, включенная в Full Profile
-   Все возможности, включая те, что не в Lite

**Дополнительные возможности:**

```java
// Асинхронные методы
@Stateless
public class ReportService {
    @Asynchronous
    public Future<Report> generateReport(ReportParams params) {
        // Долгая операция
        return new AsyncResult<>(report);
    }
}

// Message-Driven Beans
@MessageDriven(activationConfig = {
    @ActivationConfigProperty(propertyName = "destinationType", 
                             propertyValue = "javax.jms.Queue"),
    @ActivationConfigProperty(propertyName = "destination", 
                             propertyValue = "jms/OrderQueue")
})
public class OrderProcessor implements MessageListener {
    @Override
    public void onMessage(Message message) {
        // Обработка сообщения
    }
}

// Удаленные интерфейсы
@Remote
public interface RemoteCalculator {
    int add(int a, int b);
}

@Stateless
public class CalculatorBean implements RemoteCalculator {
    @Override
    public int add(int a, int b) {
        return a + b;
    }
}

// Timer Service
@Stateless
public class ScheduledTask {
    @Inject
    private TimerService timerService;
    
    public void startTimer() {
        timerService.createTimer(5000, "Order reminder");
    }
    
    @Timeout
    public void handleTimeout(Timer timer) {
        System.out.println(timer.getInfo());
    }
}

// WebService endpoints
@WebService
@Stateless
public class OrderWebService {
    @WebMethod
    public Order getOrder(Long id) { }
}
```

### Когда использовать?

**Используй EJB Lite если:**

-   Разработка простого веб-приложения
-   Нет необходимости в асинхронных операциях
-   Нет интеграции с очередями сообщений
-   Приложение работает на одном сервере

**Используй EJB Full если:**

-   Высоконагруженная система
-   Нужна асинхронная обработка
-   Нужна интеграция с JMS очередями
-   Нужны Web Services
-   Требуется распределенная обработка (удаленные интерфейсы)
-   Нужны запланированные задачи (Timer)

---

## 11. Работа с электронной почтой в Java EE

### JavaMail API

**JavaMail** — это API для отправки и получения электронной почты в Java.

### Основные компоненты

**1. Session**

-   Устанавливает сеанс подключения к почтовому серверу
-   Хранит конфигурацию (SMTP хост, порт и т.д.)

**2. Message**

-   Представляет электронное письмо
-   Содержит адресатов, тему, содержание

**3. Transport**

-   Отправляет сообщение на почтовый сервер

**4. Store**

-   Подключается к почтовому серверу для получения писем
-   Позволяет читать письма

### Пример: Отправка письма

```java
@Stateless
public class EmailService {
    
    public void sendEmail(String to, String subject, String body) {
        // Конфигурация подключения
        Properties props = new Properties();
        props.put("mail.smtp.host", "smtp.gmail.com");
        props.put("mail.smtp.port", "587");
        props.put("mail.smtp.auth", "true");
        props.put("mail.smtp.starttls.enable", "true");
        props.put("mail.smtp.starttls.required", "true");
        props.put("mail.smtp.connectiontimeout", "5000");
        props.put("mail.smtp.timeout", "5000");
        
        // Создание сеанса
        Session session = Session.getInstance(props, new Authenticator() {
            @Override
            protected PasswordAuthentication getPasswordAuthentication() {
                return new PasswordAuthentication("your-email@gmail.com", "app-password");
            }
        });
        
        try {
            // Создание сообщения
            Message message = new MimeMessage(session);
            message.setFrom(new InternetAddress("your-email@gmail.com"));
            message.setRecipients(Message.RecipientType.TO, 
                                InternetAddress.parse(to));
            message.setSubject(subject);
            message.setText(body);
            
            // Отправка
            Transport.send(message);
            System.out.println("Email sent successfully!");
            
        } catch (MessagingException e) {
            e.printStackTrace();
        }
    }
}
```

### Пример: Отправка HTML письма с вложением

```java
@Stateless
public class AdvancedEmailService {
    
    public void sendHtmlEmailWithAttachment(String to, String subject, 
                                           String htmlContent, File attachment) {
        Properties props = new Properties();
        props.put("mail.smtp.host", "smtp.gmail.com");
        props.put("mail.smtp.port", "587");
        props.put("mail.smtp.auth", "true");
        props.put("mail.smtp.starttls.enable", "true");
        
        Session session = Session.getInstance(props, new Authenticator() {
            @Override
            protected PasswordAuthentication getPasswordAuthentication() {
                return new PasswordAuthentication("your-email@gmail.com", "app-password");
            }
        });
        
        try {
            Message message = new MimeMessage(session);
            message.setFrom(new InternetAddress("your-email@gmail.com"));
            message.setRecipients(Message.RecipientType.TO, 
                                InternetAddress.parse(to));
            message.setSubject(subject);
            
            // Создание Multipart сообщения
            MimeMultipart multipart = new MimeMultipart();
            
            // HTML часть
            MimeBodyPart htmlPart = new MimeBodyPart();
            htmlPart.setContent(htmlContent, "text/html; charset=utf-8");
            multipart.addBodyPart(htmlPart);
            
            // Вложение
            MimeBodyPart attachmentPart = new MimeBodyPart();
            attachmentPart.attachFile(attachment);
            multipart.addBodyPart(attachmentPart);
            
            message.setContent(multipart);
            
            Transport.send(message);
            System.out.println("Email with attachment sent!");
            
        } catch (MessagingException | IOException e) {
            e.printStackTrace();
        }
    }
}
```

### Получение писем через IMAP

```java
@Stateless
public class EmailReceiver {
    
    public void receiveEmails() {
        Properties props = new Properties();
        props.put("mail.imap.host", "imap.gmail.com");
        props.put("mail.imap.port", "993");
        props.put("mail.imap.starttls.enable", "true");
        props.put("mail.imap.starttls.required", "true");
        
        Session session = Session.getInstance(props);
        
        try {
            // Подключение к IMAP серверу
            Store store = session.getStore("imaps");
            store.connect("imap.gmail.com", "your-email@gmail.com", "app-password");
            
            // Открытие папки входящих
            Folder inbox = store.getFolder("INBOX");
            inbox.open(Folder.READ_ONLY);
            
            Message[] messages = inbox.getMessages();
            
            // Чтение писем
            for (Message message : messages) {
                System.out.println("From: " + message.getFrom()[0]);
                System.out.println("Subject: " + message.getSubject());
                System.out.println("Text: " + message.getContent());
                System.out.println("---");
            }
            
            inbox.close();
            store.close();
            
        } catch (MessagingException e) {
            e.printStackTrace();
        }
    }
}
```

### Использование через JNDI

В production используют JNDI ресурсы вместо hardcode:

```java
@Stateless
public class EmailServiceWithJNDI {
    
    @Resource(name = "mail/gmail")
    private Session mailSession;
    
    public void sendEmail(String to, String subject, String body) {
        try {
            Message message = new MimeMessage(mailSession);
            message.setFrom(new InternetAddress("your-email@gmail.com"));
            message.setRecipients(Message.RecipientType.TO, 
                                InternetAddress.parse(to));
            message.setSubject(subject);
            message.setText(body);
            
            Transport.send(message);
            
        } catch (MessagingException e) {
            e.printStackTrace();
        }
    }
}
```

Конфигурация в `glassfish-resources.xml`:

```xml
<mail-resource
    jndi-name="mail/gmail"
    host="smtp.gmail.com"
    user="your-email@gmail.com"
    password="app-password"
    from="your-email@gmail.com"
    port="587"
    protocol="smtp"
    enabled="true"
    auth="true"
    transport-protocol="smtp">
    <property name="mail.smtp.starttls.enable" value="true"/>
    <property name="mail.smtp.auth" value="true"/>
</mail-resource>
```

---

## 12. JMS (Java Message Service)

### Что такое JMS?

**JMS (Java Message Service)** — это API для асинхронной передачи сообщений между компонентами приложения или между приложениями.

**Преимущества JMS:**

-   **Асинхронность** — отправитель не ждет получателя
-   **Надежность** — сообщения сохраняются, пока не будут обработаны
-   **Развязка** — отправитель и получатель слабо связаны
-   **Масштабируемость** — легко добавить обработчиков

### Два способа обмена сообщениями

**1. Point-to-Point (Queues)**

Модель: **Один отправитель → Очередь → Один получатель**

```
Producer → Queue → Consumer
           ↓ (сообщение остается в очереди)
           ↓ (пока Consumer не получит)
```

**Характеристики:**

-   Сообщение обрабатывается одним потребителем
-   Если потребителей несколько, один из них получит сообщение
-   Если потребителя нет, сообщение ждет

**Пример:**

```java
// Producer (отправитель)
@Stateless
public class OrderProducer {
    @Resource(name = "jms/OrderQueue")
    private Queue queue;
    
    @Inject
    private JMSContext context;
    
    public void sendOrder(Order order) {
        context.createProducer()
            .send(queue, order);
        System.out.println("Order sent to queue");
    }
}

// Consumer (получатель)
@MessageDriven(activationConfig = {
    @ActivationConfigProperty(propertyName = "destinationType", 
                             propertyValue = "javax.jms.Queue"),
    @ActivationConfigProperty(propertyName = "destination", 
                             propertyValue = "jms/OrderQueue")
})
public class OrderConsumer implements MessageListener {
    @Override
    public void onMessage(Message message) {
        try {
            if (message instanceof ObjectMessage) {
                ObjectMessage objMessage = (ObjectMessage) message;
                Order order = (Order) objMessage.getObject();
                System.out.println("Processing order: " + order.getId());
                // Обработка заказа
            }
        } catch (JMSException e) {
            e.printStackTrace();
        }
    }
}
```

**2. Pub-Sub (Topics)**

Модель: **Один отправитель → Топик → Много подписчиков**

```
Producer → Topic → Subscriber1
            ↓  → Subscriber2
            ↓  → Subscriber3
```

**Характеристики:**

-   Сообщение отправляется всем подписчикам одновременно
-   Подписчики должны быть подписаны ДО отправки сообщения
-   Если подписчика нет, сообщение теряется (если нет durable subscription)

**Пример:**

```java
// Durable Topic Subscriber
@MessageDriven(activationConfig = {
    @ActivationConfigProperty(propertyName = "destinationType", 
                             propertyValue = "javax.jms.Topic"),
    @ActivationConfigProperty(propertyName = "destination", 
                             propertyValue = "jms/UserEventsTopic"),
    @ActivationConfigProperty(propertyName = "subscriptionDurability", 
                             propertyValue = "Durable"),
    @ActivationConfigProperty(propertyName = "clientId", 
                             propertyValue = "EmailService"),
    @ActivationConfigProperty(propertyName = "subscriptionName", 
                             propertyValue = "EmailServiceSubscription")
})
public class UserEventEmailListener implements MessageListener {
    @Inject
    private EmailService emailService;
    
    @Override
    public void onMessage(Message message) {
        try {
            if (message instanceof TextMessage) {
                TextMessage txtMessage = (TextMessage) message;
                String event = txtMessage.getText();
                System.out.println("Email service received: " + event);
                emailService.sendNotification(event);
            }
        } catch (JMSException e) {
            e.printStackTrace();
        }
    }
}

// Еще один подписчик
@MessageDriven(activationConfig = {
    @ActivationConfigProperty(propertyName = "destinationType", 
                             propertyValue = "javax.jms.Topic"),
    @ActivationConfigProperty(propertyName = "destination", 
                             propertyValue = "jms/UserEventsTopic"),
    @ActivationConfigProperty(propertyName = "subscriptionDurability", 
                             propertyValue = "Durable"),
    @ActivationConfigProperty(propertyName = "clientId", 
                             propertyValue = "LogService"),
    @ActivationConfigProperty(propertyName = "subscriptionName", 
                             propertyValue = "LogServiceSubscription")
})
public class UserEventLogListener implements MessageListener {
    @Inject
    private Logger logger;
    
    @Override
    public void onMessage(Message message) {
        try {
            if (message instanceof TextMessage) {
                TextMessage txtMessage = (TextMessage) message;
                String event = txtMessage.getText();
                logger.info("Event logged: " + event);
            }
        } catch (JMSException e) {
            e.printStackTrace();
        }
    }
}
```

### JMS Context и Producer

```java
@Stateless
public class OrderService {
    @Inject
    private JMSContext context;
    
    @Resource(name = "jms/OrderQueue")
    private Queue orderQueue;
    
    @Resource(name = "jms/NotificationTopic")
    private Topic notificationTopic;
    
    public void createOrder(Order order) {
        // Сохранение заказа
        // ...
        
        // Отправка в очередь для обработки
        context.createProducer()
            .send(orderQueue, order);
        
        // Уведомление подписчиков
        context.createProducer()
            .send(notificationTopic, "Order created: " + order.getId());
    }
    
    // С указанием приоритета
    public void sendUrgentOrder(Order order) {
        context.createProducer()
            .setPriority(9)  // Высокий приоритет
            .setTimeToLive(60000)  // 60 секунд на обработку
            .send(orderQueue, order);
    }
}
```

### Типы JMS сообщений

```java
public class JmsMessageTypes {
    
    @Inject
    private JMSContext context;
    
    @Resource(name = "jms/TestQueue")
    private Queue queue;
    
    // TextMessage - строка
    public void sendText(String text) {
        context.createProducer()
            .send(queue, text);
    }
    
    // ObjectMessage - сериализуемый объект
    public void sendObject(Serializable obj) {
        context.createProducer()
            .send(queue, obj);
    }
    
    // BytesMessage - массив байтов
    public void sendBytes(byte[] data) {
        BytesMessage msg = context.createBytesMessage();
        msg.writeBytes(data);
        context.createProducer().send(queue, msg);
    }
    
    // MapMessage - key-value пары
    public void sendMap(Map<String, Object> data) {
        MapMessage msg = context.createMapMessage();
        for (Map.Entry<String, Object> entry : data.entrySet()) {
            msg.setObject(entry.getKey(), entry.getValue());
        }
        context.createProducer().send(queue, msg);
    }
    
    // StreamMessage - поток данных
    public void sendStream(String text, int number) {
        StreamMessage msg = context.createStreamMessage();
        msg.writeString(text);
        msg.writeInt(number);
        context.createProducer().send(queue, msg);
    }
}
```

---

## 13. Реализация очередей сообщений

### JMS Provider Configuration (GlassFish)

**1. Создание JMS ресурсов через admin console**

или через `asadmin` команды:

```bash
# Создание Connection Factory
asadmin create-jms-resource --restype javax.jms.ConnectionFactory 
  jms/OrderConnectionFactory

# Создание Queue
asadmin create-jms-resource --restype javax.jms.Queue 
  --property PhysicalDestinationName=OrderQueuePhysical 
  jms/OrderQueue

# Создание Topic
asadmin create-jms-resource --restype javax.jms.Topic 
  --property PhysicalDestinationName=NotificationTopicPhysical 
  jms/NotificationTopic
```

**2. Конфигурация через glassfish-resources.xml**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<resources>
    <!-- Connection Factory -->
    <connector-resource 
        jndi-name="jms/OrderConnectionFactory"
        pool-name="jms/OrderConnectionFactoryPool"/>
    
    <connector-connection-pool
        name="jms/OrderConnectionFactoryPool"
        connection-definition-name="javax.jms.ConnectionFactory"
        resource-adapter-name="jmsra"/>
    
    <!-- Queue -->
    <admin-object-resource
        jndi-name="jms/OrderQueue"
        res-type="javax.jms.Queue"
        res-adapter-name="jmsra"
        property="PhysicalDestinationName=OrderQueuePhysical"/>
    
    <!-- Topic -->
    <admin-object-resource
        jndi-name="jms/NotificationTopic"
        res-type="javax.jms.Topic"
        res-adapter-name="jmsra"
        property="PhysicalDestinationName=NotificationTopicPhysical"/>
</resources>
```

### Message-Driven Bean с продвинутой конфигурацией

```java
@MessageDriven(
    activationConfig = {
        @ActivationConfigProperty(
            propertyName = "destinationType",
            propertyValue = "javax.jms.Queue"
        ),
        @ActivationConfigProperty(
            propertyName = "destination",
            propertyValue = "jms/OrderQueue"
        ),
        @ActivationConfigProperty(
            propertyName = "acknowledgeMode",
            propertyValue = "Auto"  // или "Dups-ok-acknowledge"
        ),
        @ActivationConfigProperty(
            propertyName = "messageSelector",
            propertyValue = "priority > 5"  // Фильтр сообщений
        ),
        @ActivationConfigProperty(
            propertyName = "maxPoolSize",
            propertyValue = "10"  // Количество параллельных обработчиков
        )
    },
    name = "OrderProcessingBean"
)
public class OrderProcessingBean implements MessageListener {
    
    @Inject
    private OrderService orderService;
    
    @Inject
    private Logger logger;
    
    @Override
    public void onMessage(Message message) {
        try {
            if (message instanceof ObjectMessage) {
                ObjectMessage objMsg = (ObjectMessage) message;
                Order order = (Order) objMsg.getObject();
                
                logger.info("Processing order: " + order.getId());
                orderService.process(order);
                
                // Не нужно вызывать message.acknowledge()
                // контейнер сделает это автоматически (Auto mode)
                
            }
        } catch (JMSException e) {
            logger.severe("Error processing message: " + e.getMessage());
            // При исключении сообщение вернется в очередь
            throw new RuntimeException(e);
        }
    }
}
```

---

## 14. Способы доставки сообщений до клиента

### 1. Pull Model (Polling)

Клиент сам запрашивает сообщения:

```java
// Konsumer вручную запрашивает сообщения
@Stateless
public class OrderConsumer {
    @Inject
    private JMSContext context;
    
    @Resource(name = "jms/OrderQueue")
    private Queue orderQueue;
    
    public Order getNextOrder() {
        // Получить следующее сообщение
        JMSConsumer consumer = context.createConsumer(orderQueue);
        Message message = consumer.receiveNoWait();  // Не блокирует
        
        if (message instanceof ObjectMessage) {
            try {
                return (Order) ((ObjectMessage) message).getObject();
            } catch (JMSException e) {
                throw new RuntimeException(e);
            }
        }
        return null;
    }
    
    // С timeout
    public Order getNextOrderWithTimeout(long timeoutMs) {
        JMSConsumer consumer = context.createConsumer(orderQueue);
        Message message = consumer.receive(timeoutMs);  // Ждет до timeout
        
        if (message instanceof ObjectMessage) {
            try {
                return (Order) ((ObjectMessage) message).getObject();
            } catch (JMSException e) {
                throw new RuntimeException(e);
            }
        }
        return null;
    }
}
```

**Когда использовать:**

-   Обработка по требованию
-   Низкая частота сообщений
-   Нужен контроль над временем обработки

---

### 2. Push Model (Message-Driven Bean)

Контейнер автоматически вызывает обработчик при получении сообщения:

```java
@MessageDriven(activationConfig = {
    @ActivationConfigProperty(propertyName = "destinationType", 
                             propertyValue = "javax.jms.Queue"),
    @ActivationConfigProperty(propertyName = "destination", 
                             propertyValue = "jms/OrderQueue")
})
public class OrderProcessingBean implements MessageListener {
    
    @Inject
    private OrderService orderService;
    
    @Override
    public void onMessage(Message message) {
        // Автоматически вызывается при получении сообщения
        try {
            if (message instanceof ObjectMessage) {
                Order order = (Order) ((ObjectMessage) message).getObject();
                orderService.process(order);
            }
        } catch (JMSException e) {
            throw new RuntimeException(e);
        }
    }
}
```

**Когда использовать:**

-   Высокая частота сообщений
-   Нужна быстрая реакция
-   Большой объем обработки

---

### 3. WebSocket (Real-time Push к браузеру)

Отправка событий на клиент в браузер через WebSocket:

```java
// Server endpoint
@ServerEndpoint("/notifications")
public class NotificationEndpoint {
    private static Set<Session> sessions = Collections.synchronizedSet(new HashSet<>());
    
    @OnOpen
    public void onOpen(Session session) {
        sessions.add(session);
        System.out.println("Client connected: " + session.getId());
    }
    
    @OnClose
    public void onClose(Session session) {
        sessions.remove(session);
        System.out.println("Client disconnected: " + session.getId());
    }
    
    @OnError
    public void onError(Session session, Throwable throwable) {
        sessions.remove(session);
        System.out.println("Error: " + throwable.getMessage());
    }
    
    public static void broadcast(String message) {
        for (Session session : sessions) {
            try {
                session.getBasicRemote().sendText(message);
            } catch (IOException e) {
                System.out.println("Error sending message: " + e.getMessage());
            }
        }
    }
}

// Service отправляет уведомление
@Stateless
public class OrderService {
    public void createOrder(Order order) {
        // Сохранение заказа
        // ...
        
        // Отправка всем подключенным клиентам
        NotificationEndpoint.broadcast("New order: " + order.getId());
    }
}
```

**Client JavaScript:**

```javascript
const ws = new WebSocket("ws://localhost:8080/app/notifications");

ws.onopen = function(event) {
    console.log("Connected to notification server");
};

ws.onmessage = function(event) {
    const notification = event.data;
    showNotification(notification);
};

ws.onerror = function(event) {
    console.error("WebSocket error: " + event);
};

ws.onclose = function(event) {
    console.log("Disconnected from notification server");
};
```

---

### 4. Server-Sent Events (SSE)

HTTP-based streaming:

```java
@Stateless
public class EventService {
    @Inject
    private Event<String> orderEvent;
    
    public void publishOrder(Order order) {
        orderEvent.fire("Order created: " + order.getId());
    }
}

@Path("/events")
public class EventEndpoint {
    
    @Inject
    private OrderService orderService;
    
    @GET
    @Produces(MediaType.SERVER_SENT_EVENTS)
    public void subscribe(@Context SseEventSink sink) {
        new Thread(() -> {
            try {
                // Отправка events
                for (int i = 0; i < 10; i++) {
                    Thread.sleep(1000);
                    sink.send(SseEvent.builder()
                        .id(String.valueOf(i))
                        .name("update")
                        .data("Event " + i)
                        .build());
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }).start();
    }
}
```

**Client JavaScript:**

```javascript
const eventSource = new EventSource("http://localhost:8080/app/events");

eventSource.onmessage = function(event) {
    console.log("Event received: " + event.data);
};

eventSource.onerror = function(event) {
    console.error("Error: " + event);
    eventSource.close();
};
```

---

## 15. Message-Driven Beans

### Что такое Message-Driven Bean?

**Message-Driven Bean (MDB)** — это компонент EJB, который обрабатывает JMS сообщения асинхронно.

**Характеристики:**

-   Реагирует на сообщения из очереди или топика
-   Нет методов, которые можно вызвать клиентом
-   Контейнер создает пул экземпляров для обработки сообщений
-   Поддерживает транзакции, безопасность, масштабируемость

### Базовая структура

```java
@MessageDriven(
    activationConfig = {
        @ActivationConfigProperty(
            propertyName = "destinationType",
            propertyValue = "javax.jms.Queue"
        ),
        @ActivationConfigProperty(
            propertyName = "destination",
            propertyValue = "jms/OrderQueue"
        )
    }
)
public class OrderProcessingMDB implements MessageListener {
    
    @Inject
    private OrderService orderService;
    
    @Inject
    private Logger logger;
    
    @Override
    public void onMessage(Message message) {
        try {
            if (message instanceof ObjectMessage) {
                Order order = (Order) ((ObjectMessage) message).getObject();
                logger.info("Processing order: " + order.getId());
                orderService.process(order);
                logger.info("Order processed successfully");
            }
        } catch (JMSException e) {
            logger.severe("Error: " + e.getMessage());
            throw new RuntimeException(e);  // Вернуть в очередь
        }
    }
}
```

### Продвинутое использование

**1. Обработка разных типов сообщений**

```java
@MessageDriven(activationConfig = {
    @ActivationConfigProperty(propertyName = "destinationType", 
                             propertyValue = "javax.jms.Queue"),
    @ActivationConfigProperty(propertyName = "destination", 
                             propertyValue = "jms/EventQueue")
})
public class EventProcessingMDB implements MessageListener {
    
    @Inject
    private OrderService orderService;
    
    @Inject
    private UserService userService;
    
    @Override
    public void onMessage(Message message) {
        try {
            if (message instanceof ObjectMessage) {
                ObjectMessage objMsg = (ObjectMessage) message;
                Object obj = objMsg.getObject();
                
                if (obj instanceof Order) {
                    orderService.process((Order) obj);
                } else if (obj instanceof User) {
                    userService.register((User) obj);
                }
            } else if (message instanceof TextMessage) {
                TextMessage txtMsg = (TextMessage) message;
                String event = txtMsg.getText();
                System.out.println("Event: " + event);
            }
        } catch (JMSException e) {
            throw new RuntimeException(e);
        }
    }
}
```

**2. Dead Letter Queue (DLQ)**

Обработка сообщений, которые не могут быть обработаны:

```java
@MessageDriven(activationConfig = {
    @ActivationConfigProperty(propertyName = "destinationType", 
                             propertyValue = "javax.jms.Queue"),
    @ActivationConfigProperty(propertyName = "destination", 
                             propertyValue = "jms/DeadLetterQueue")
})
public class DeadLetterMDB implements MessageListener {
    
    @Inject
    private AlertService alertService;
    
    @Override
    public void onMessage(Message message) {
        try {
            String originalQueue = message.getStringProperty("JMSXDeadLetterQueue");
            int redeliveryCount = message.getIntProperty("JMSXDeliveryCount");
            
            alertService.sendAlert("Message failed after " + redeliveryCount + 
                                 " attempts in queue: " + originalQueue);
            
            // Сохранение в БД для последующего анализа
            // ...
            
        } catch (JMSException e) {
            e.printStackTrace();
        }
    }
}
```

**3. Retry Logic**

```java
@Stateless
public class OrderService {
    
    @Inject
    private JMSContext context;
    
    @Resource(name = "jms/OrderQueue")
    private Queue retryQueue;
    
    public void processWithRetry(Order order, int retryCount) {
        try {
            // Попытка обработки
            // ...
        } catch (Exception e) {
            if (retryCount < 3) {
                // Переотправить в очередь на повторную попытку
                context.createProducer()
                    .setDeliveryDelay(5000)  // Ждать 5 секунд перед повтором
                    .send(retryQueue, order);
            } else {
                // Отправить в DLQ
                // ...
            }
        }
    }
}
```

---

## 16. Понятие транзакции

### Что такое транзакция?

**Транзакция** — это логическая единица работы, которая должна либо полностью выполниться, либо не выполниться вообще.

**ACID свойства:**

1.  **Atomicity (Атомарность)**
    
    -   Транзакция либо полностью выполняется, либо не выполняется вообще
    -   Нет частичного выполнения
    
    ```
    Вопрос: Переводим 1000 рублей с счета A на счет B
    
    Сценарий БЕЗ транзакции:
    1. Снимаем 1000 со счета A ✓ (счет A: -1000)
    2. Ошибка в сети! ✗
    3. Добавляем на счет B (не выполняется)
    Результат: Деньги потеряны!
    
    Сценарий С транзакцией:
    1. Начало транзакции
    2. Снимаем 1000 со счета A
    3. Ошибка в сети!
    4. ROLLBACK всех изменений
    Результат: Счета не изменились, деньги на месте
    ```
    
2.  **Consistency (Согласованность)**
    
    -   БД переходит из одного согласованного состояния в другое
    -   Соблюдаются все ограничения и правила
    
    ```
    Пример: Сумма всех счетов должна быть постоянной
    
    Начало: Счет A = 1000, Счет B = 2000, Сумма = 3000
    
    Транзакция: Перевод 500 с A на B
    
    Конец: Счет A = 500, Счет B = 2500, Сумма = 3000 ✓
    ```
    
3.  **Isolation (Изоляция)**
    
    -   Транзакции не влияют друг на друга
    -   Изменения одной транзакции не видны другой до коммита
    
    ```
    Транзакция 1: Читает Счет A (1000)
    Транзакция 2: Изменяет Счет A на 1500
    Транзакция 2: COMMIT
    Транзакция 1: Видит ли 1500 или 1000?
    
    Это зависит от уровня изоляции!
    ```
    
4.  **Durability (Стойкость)**
    
    -   После коммита данные постоянно сохраняются
    -   Даже при сбое питания или системы
    
    ```
    Транзакция: Добавляем пользователя в БД
    COMMIT
    Сбой питания!
    Результат: Пользователь остался в БД
    ```
    

### Простой пример

```java
@Stateless
public class BankService {
    
    @PersistenceContext
    private EntityManager em;
    
    @Transactional  // Контейнер управляет транзакцией
    public void transferMoney(Account fromAccount, Account toAccount, 
                             BigDecimal amount) {
        // Начало транзакции
        
        // Снятие со счета
        fromAccount.setBalance(fromAccount.getBalance().subtract(amount));
        em.merge(fromAccount);
        
        // Может быть ошибка здесь!
        if (toAccount.isBlocked()) {
            throw new RuntimeException("Account is blocked!");
        }
        
        // Пополнение счета
        toAccount.setBalance(toAccount.getBalance().add(amount));
        em.merge(toAccount);
        
        // Конец транзакции (COMMIT)
        // Если ошибка → ROLLBACK всех изменений
    }
}
```

**При ошибке:**

```
1. Снятие со счета A (запись в памяти)
2. Ошибка: Account is blocked!
3. ROLLBACK - оба счета вернулись в исходное состояние
```

---

## 17. Управление транзакциями в Java EE

### Container-Managed Transactions (CMT)

Контейнер автоматически управляет транзакциями.

**Основные аннотации:**

```java
@Transactional  // С Java EE 7
public void methodName() {
    // Контейнер управляет транзакцией
}
```

**Или для EJB (до Java EE 7):**

```java
@Stateless
public class OrderService {
    
    @PersistenceContext
    private EntityManager em;
    
    // Аннотация @TransactionAttribute
    @TransactionAttribute(TransactionAttributeType.REQUIRED)  // По умолчанию
    public void createOrder(Order order) {
        // Если есть активная транзакция, используем её
        // Если нет, контейнер создает новую
        em.persist(order);
    }
}
```

### Типы транзакций (TransactionAttributeType)

**1. REQUIRED (по умолчанию)**

```java
@TransactionAttribute(TransactionAttributeType.REQUIRED)
public void method() {
    // Использует существующую транзакцию или создает новую
}
```

**Сценарий:**

```
Если клиент вызвал в транзакции → используется её
Если клиент вызвал БЕЗ транзакции → создается новая
```

**2. REQUIRES_NEW**

```java
@TransactionAttribute(TransactionAttributeType.REQUIRES_NEW)
public void method() {
    // Всегда создает новую транзакцию
    // Старая транзакция приостанавливается
}
```

**Сценарий:**

```
Старая транзакция (T1)
  ↓
Вызов метода с REQUIRES_NEW
  ↓
Создание новой транзакции (T2)
  ↓
T1 приостановлена
  ↓
T2 выполняется
  ↓
T2 коммитится независимо от T1
  ↓
T1 возобновляется
```

**Пример:**

```java
@Stateless
public class OrderService {
    
    @Inject
    private AuditService auditService;
    
    @Transactional(REQUIRED)
    public void createOrder(Order order) {
        // Основная транзакция
        em.persist(order);
        
        // Даже если createOrder откатится,
        // аудит останется записан
        auditService.logAction("Order created");
    }
}

@Stateless
public class AuditService {
    
    @Transactional(REQUIRES_NEW)
    public void logAction(String action) {
        // Независимая транзакция
        em.persist(new AuditLog(action));
    }
}
```

**3. SUPPORTS**

```java
@TransactionAttribute(TransactionAttributeType.SUPPORTS)
public void method() {
    // Если есть транзакция, участвует в ней
    // Если нет, выполняется БЕЗ транзакции
}
```

**4. NOT_SUPPORTED**

```java
@TransactionAttribute(TransactionAttributeType.NOT_SUPPORTED)
public void method() {
    // Никогда не использует транзакции
    // Если есть, приостанавливает её
}
```

**Пример:**

```java
@Stateless
public class ReportService {
    
    @Transactional(NOT_SUPPORTED)
    public List<Report> getAllReports() {
        // Только чтение данных БЕЗ транзакции
        // Быстрее, чем с транзакцией
        return em.createQuery("SELECT r FROM Report r", Report.class)
            .getResultList();
    }
}
```

**5. MANDATORY**

```java
@TransactionAttribute(TransactionAttributeType.MANDATORY)
public void method() {
    // Метод ДОЛЖЕН быть вызван в контексте транзакции
    // Если нет → выбрасывает исключение
}
```

**Пример:**

```java
@Stateless
public class OrderProcessor {
    
    @Transactional(MANDATORY)
    public void processOrder(Order order) {
        // Этот метод ДОЛЖЕН быть вызван из транзакции
    }
    
    @Transactional(REQUIRED)
    public void createAndProcess(Order order) {
        em.persist(order);
        processOrder(order);  // OK, есть транзакция
    }
    
    public void directCall(Order order) {
        processOrder(order);  // ✗ Исключение! Нет транзакции
    }
}
```

**6. NEVER**

```java
@TransactionAttribute(TransactionAttributeType.NEVER)
public void method() {
    // Метод НЕ должен быть в транзакции
    // Если есть → выбрасывает исключение
}
```

### Обработка исключений в транзакциях

**Checked exceptions (не откатывают):**

```java
@Transactional
public void methodWithCheckedException() throws IOException {
    em.persist(order);
    // Если IOException → COMMIT (откат НЕ происходит!)
}
```

**Runtime exceptions (откатывают):**

```java
@Transactional
public void methodWithRuntimeException() {
    em.persist(order);
    if (order.getPrice() < 0) {
        throw new IllegalArgumentException("Invalid price");
        // Если выброшено → ROLLBACK
    }
}
```

**Контроль поведения:**

```java
@Transactional(
    rollbackOn = {IOException.class, TimeoutException.class},
    noRollbackOn = {ValidationException.class}
)
public void complexMethod() throws Exception {
    em.persist(order);
    // IOException → ROLLBACK
    // TimeoutException → ROLLBACK
    // ValidationException → COMMIT
}
```

### Bean-Managed Transactions (BMT)

Приложение сами управляют транзакциями:

```java
@Stateless
@TransactionManagement(TransactionManagementType.BEAN)
public class ManualTransactionService {
    
    @Resource
    private UserTransaction userTransaction;
    
    @PersistenceContext
    private EntityManager em;
    
    public void transferMoney(Account from, Account to, BigDecimal amount) 
            throws Exception {
        try {
            // Начало транзакции вручную
            userTransaction.begin();
            
            from.setBalance(from.getBalance().subtract(amount));
            em.merge(from);
            
            // Проверка
            if (to.isInvalid()) {
                throw new RuntimeException("Invalid account");
            }
            
            to.setBalance(to.getBalance().add(amount));
            em.merge(to);
            
            // Фиксация транзакции вручную
            userTransaction.commit();
            
        } catch (Exception e) {
            // Откат вручную
            userTransaction.rollback();
            throw e;
        }
    }
}
```

**Сравнение CMT vs BMT:**

Характеристика

CMT

BMT

**Управление**

Контейнер

Приложение

**Простота**

Простая (@Transactional)

Сложная

**Гибкость**

Ограниченная

Полная

**Производительность**

Хорошая

Может быть лучше

**Когда использовать**

Большинство случаев

Сложная логика

---

## 18. JTA (Java Transaction API)

**JTA** — это API для управления распределенными транзакциями.

### Основные компоненты

**1. UserTransaction**

```java
@Resource
private UserTransaction userTransaction;

public void doSomething() throws Exception {
    userTransaction.begin();
    try {
        // Операции
        userTransaction.commit();
    } catch (Exception e) {
        userTransaction.rollback();
        throw e;
    }
}
```

**2. TransactionManager**

```java
// Используется контейнером и приложениями для управления транзакциями
// Обычно не используется напрямую
```

**3. Resource Manager (БД)**

```
Когда в транзакции участвует несколько баз данных,
JTA координирует commit/rollback на всех.
```

### Двухфазный коммит (Two-Phase Commit)

```
Фаза 1: PREPARE (подготовка)
  ↓ Координатор: "Готовы ли вы коммитить?"
  ↓ DB1: "ДА, я готова"
  ↓ DB2: "ДА, я готова"

Фаза 2: COMMIT (фиксация)
  ↓ Координатор: "Коммитьте!"
  ↓ DB1: "Коммитим..." ✓
  ↓ DB2: "Коммитим..." ✓
```

**Пример:**

```java
@Stateless
public class DistributedTransactionService {
    
    @PersistenceContext(name = "db1")
    private EntityManager em1;
    
    @PersistenceContext(name = "db2")
    private EntityManager em2;
    
    @Transactional  // JTA контролирует обе БД
    public void transferAcrossDatabases(Long userId, BigDecimal amount) {
        // Операция на DB1
        User user1 = em1.find(User.class, userId);
        user1.setBalance(user1.getBalance().subtract(amount));
        em1.merge(user1);
        
        // Операция на DB2
        Account account2 = em2.find(Account.class, userId);
        account2.setAmount(account2.getAmount().add(amount));
        em2.merge(account2);
        
        // JTA двухфазный коммит:
        // Фаза 1: Обе БД готовы?
        // Фаза 2: Коммитим на обеих или откатываем на обеих
    }
}
```

### Изоляция (Isolation Levels)

**1. READ_UNCOMMITTED**

```
Транзакция видит грязные чтения (dirty reads)

T1: UPDATE Account SET balance = 1000
T2: SELECT balance (видит 1000)
T1: ROLLBACK (balance вернулся на 500)
T2: Видела неправильное значение! (грязное чтение)
```

**2. READ_COMMITTED (по умолчанию)**

```
Транзакция видит только закоммиченные изменения

T1: UPDATE Account SET balance = 1000
T2: SELECT balance (ждет T1)
T1: COMMIT
T2: SELECT balance (видит 1000)
```

**3. REPEATABLE_READ**

```
Одна транзакция всегда видит один и тот же результат

T1: SELECT count FROM Table (результат: 5)
T2: INSERT INTO Table (добавляет запись)
T2: COMMIT
T1: SELECT count FROM Table (результат: 5, не 6!)
```

**4. SERIALIZABLE**

```
Транзакции выполняются последовательно, как если бы не было параллелизма

T1: BEGIN
T2: Ждет T1
T1: COMMIT
T2: BEGIN
```

**Как устанавливать:**

```java
// В Hibernate (JPA)
@NamedQuery(
    name = "query",
    query = "...",
    hints = {
        @QueryHint(name = "org.hibernate.readOnly", value = "true")
    }
)
public class Entity {
    // ...
}

// На уровне БД (PostgreSQL)
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

---

## 19. Веб-сервисы

### Что такое веб-сервис?

**Веб-сервис** — это программный сервис, доступный через сеть (HTTP) и использующий стандартизированные форматы обмена данными.

**Характеристики:**

-   Доступен через интернет/сеть
-   Использует стандартные протоколы (HTTP, HTTPS)
-   Использует стандартные форматы (XML, JSON)
-   Может быть вызван из любого языка программирования
-   Предоставляет интерфейс для взаимодействия

### Два основных стиля

**1. SOAP (Simple Object Access Protocol)**

-   Использует XML для обмена данными
-   Более формальный и строгий
-   Требует WSDL (Web Services Description Language)
-   Медленнее, чем REST
-   Поддерживает продвинутые функции (безопасность, transactions)

**2. REST (Representational State Transfer)**

-   Использует HTTP методы (GET, POST, PUT, DELETE)
-   Может использовать JSON или XML
-   Проще, чем SOAP
-   Быстрее
-   Лучше подходит для веб-приложений

---

## 20. JAX-RS (Java API for RESTful Web Services)

### Основные концепции

**1. @Path - определение маршрута**

```java
@Path("/users")  // Базовый путь для этого ресурса
public class UserResource {
    // Методы будут доступны по /users/...
}
```

**2. @GET, @POST, @PUT, @DELETE - HTTP методы**

```java
@Path("/users")
public class UserResource {
    
    @GET
    @Path("/{id}")
    @Produces(MediaType.APPLICATION_JSON)
    public User getUser(@PathParam("id") Long id) {
        // GET /users/123
    }
    
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public User createUser(User user) {
        // POST /users
    }
    
    @PUT
    @Path("/{id}")
    @Consumes(MediaType.APPLICATION_JSON)
    public void updateUser(@PathParam("id") Long id, User user) {
        // PUT /users/123
    }
    
    @DELETE
    @Path("/{id}")
    public void deleteUser(@PathParam("id") Long id) {
        // DELETE /users/123
    }
}
```

### Полный пример REST API

```java
@Path("/api/orders")
@RequestScoped
public class OrderResource {
    
    @Inject
    private OrderService orderService;
    
    // GET /api/orders
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getAllOrders(
            @QueryParam("page") @DefaultValue("0") int page,
            @QueryParam("size") @DefaultValue("10") int size) {
        List<Order> orders = orderService.getAllOrders(page, size);
        return Response.ok(orders).build();
    }
    
    // GET /api/orders/123
    @GET
    @Path("/{id}")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getOrder(@PathParam("id") Long id) {
        Order order = orderService.getOrder(id);
        if (order == null) {
            return Response.status(Response.Status.NOT_FOUND).build();
        }
        return Response.ok(order).build();
    }
    
    // POST /api/orders
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response createOrder(Order order) {
        Order created = orderService.createOrder(order);
        return Response.status(Response.Status.CREATED)
            .entity(created)
            .build();
    }
    
    // PUT /api/orders/123
    @PUT
    @Path("/{id}")
    @Consumes(MediaType.APPLICATION_JSON)
    public Response updateOrder(
            @PathParam("id") Long id, 
            Order order) {
        orderService.updateOrder(id, order);
        return Response.noContent().build();
    }
    
    // DELETE /api/orders/123
    @DELETE
    @Path("/{id}")
    public Response deleteOrder(@PathParam("id") Long id) {
        orderService.deleteOrder(id);
        return Response.noContent().build();
    }
    
    // GET /api/orders/123/items
    @GET
    @Path("/{id}/items")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getOrderItems(@PathParam("id") Long orderId) {
        List<Item> items = orderService.getOrderItems(orderId);
        return Response.ok(items).build();
    }
}
```

### Параметры запроса

```java
@Path("/search")
public class SearchResource {
    
    // Query parameters: /search?keyword=laptop&category=electronics
    @GET
    public Response search(
            @QueryParam("keyword") String keyword,
            @QueryParam("category") String category) {
        // Параметры из query string
        return Response.ok().build();
    }
    
    // Path parameters: /users/123
    @GET
    @Path("/users/{userId}")
    public Response getUser(@PathParam("userId") Long userId) {
        // Параметр из пути
        return Response.ok().build();
    }
    
    // Header parameters: Authorization: Bearer token123
    @GET
    public Response getProtected(
            @HeaderParam("Authorization") String authHeader) {
        // Параметр из заголовка
        return Response.ok().build();
    }
    
    // Form parameters: POST форма
    @POST
    @Consumes(MediaType.APPLICATION_FORM_URLENCODED)
    public Response postForm(
            @FormParam("username") String username,
            @FormParam("password") String password) {
        // Параметры из формы
        return Response.ok().build();
    }
    
    // Matrix parameters: /items;color=red;size=large
    @GET
    @Path("/items")
    public Response getItems(
            @MatrixParam("color") String color,
            @MatrixParam("size") String size) {
        // Параметры из matrix строки
        return Response.ok().build();
    }
}
```

### Content Negotiation

```java
@Path("/products")
public class ProductResource {
    
    @GET
    @Path("/{id}")
    @Produces({MediaType.APPLICATION_JSON, MediaType.APPLICATION_XML})
    public Product getProduct(@PathParam("id") Long id) {
        // Если клиент отправил Accept: application/json → вернуть JSON
        // Если клиент отправил Accept: application/xml → вернуть XML
        return productService.getProduct(id);
    }
    
    @POST
    @Consumes({MediaType.APPLICATION_JSON, MediaType.APPLICATION_XML})
    @Produces(MediaType.APPLICATION_JSON)
    public Response createProduct(Product product) {
        // Автоматически парсит JSON или XML в зависимости от Content-Type
        Product created = productService.createProduct(product);
        return Response.status(Response.Status.CREATED).entity(created).build();
    }
}
```

### Exception Handling

```java
public class OrderNotFoundException extends RuntimeException {
    public OrderNotFoundException(Long id) {
        super("Order not found: " + id);
    }
}

@Provider  // Регистрируем ExceptionMapper
public class OrderNotFoundMapper implements ExceptionMapper<OrderNotFoundException> {
    @Override
    public Response toResponse(OrderNotFoundException ex) {
        return Response.status(Response.Status.NOT_FOUND)
            .entity(new ErrorResponse(ex.getMessage()))
            .build();
    }
}

@Path("/orders")
public class OrderResource {
    
    @GET
    @Path("/{id}")
    public Response getOrder(@PathParam("id") Long id) {
        Order order = orderService.getOrder(id);
        if (order == null) {
            throw new OrderNotFoundException(id);  // автоматически преобразуется
        }
        return Response.ok(order).build();
    }
}
```

### Filters и Interceptors

```java
// Request Filter
@Provider
public class LoggingFilter implements ContainerRequestFilter {
    @Override
    public void filter(ContainerRequestContext requestContext) 
            throws IOException {
        System.out.println("Request: " + requestContext.getMethod() + " " +
                         requestContext.getUriInfo().getPath());
    }
}

// Response Filter
@Provider
public class CORSFilter implements ContainerResponseFilter {
    @Override
    public void filter(ContainerRequestContext requestContext, 
                      ContainerResponseContext responseContext) 
            throws IOException {
        responseContext.getHeaders().add("Access-Control-Allow-Origin", "*");
        responseContext.getHeaders().add("Access-Control-Allow-Methods", 
            "GET, POST, PUT, DELETE");
    }
}

// Writer Interceptor (сжатие ответа)
@Provider
public class GzipInterceptor implements WriterInterceptor {
    @Override
    public void aroundWriteTo(WriterInterceptorContext context) 
            throws IOException, WebApplicationException {
        context.proceed();  // Выполнить основную операцию
    }
}
```

---

## 21. JAX-WS (Java API for XML Web Services)

### SOAP Web Service

```java
@WebService
@Stateless
public class OrderWebService {
    
    @Inject
    private OrderService orderService;
    
    @WebMethod
    public Order getOrder(@WebParam(name = "id") Long id) {
        return orderService.getOrder(id);
    }
    
    @WebMethod
    public Order createOrder(@WebParam(name = "order") Order order) {
        return orderService.createOrder(order);
    }
    
    @WebMethod(exclude = true)  // Этот метод не будет доступен как веб-метод
    public void internalMethod() {
        // ...
    }
}
```

**Использование SOAP сервиса:**

```java
@WebServiceClient(
    name = "OrderWebService",
    targetNamespace = "http://example.com/services",
    wsdlLocation = "http://localhost:8080/services/OrderWebService?wsdl"
)
public class OrderWebServiceClient {
    
    private OrderWebService_Service service;
    
    public void callService() {
        service = new OrderWebService_Service();
        OrderWebService port = service.getOrderWebServicePort();
        
        Order order = port.getOrder(123L);
        System.out.println("Order: " + order);
    }
}
```

### WSDL (Web Services Description Language)

WSDL описывает SOAP сервис:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://schemas.xmlsoap.org/wsdl/">
    <types>
        <!-- Типы данных (XSD схема) -->
        <xsd:schema targetNamespace="http://example.com/services">
            <xsd:element name="Order">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="id" type="xsd:long"/>
                        <xsd:element name="totalAmount" type="xsd:decimal"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
    </types>
    
    <message name="GetOrderRequest">
        <part name="id" type="xsd:long"/>
    </message>
    
    <message name="GetOrderResponse">
        <part name="order" type="tns:Order"/>
    </message>
    
    <portType name="OrderWebService">
        <operation name="getOrder">
            <input message="tns:GetOrderRequest"/>
            <output message="tns:GetOrderResponse"/>
        </operation>
    </portType>
    
    <binding name="OrderWebServiceBinding" type="tns:OrderWebService">
        <soap:binding transport="http://schemas.xmlsoap.org/soap/http"/>
        <operation name="getOrder">
            <soap:operation soapAction="getOrder"/>
        </operation>
    </binding>
    
    <service name="OrderWebService">
        <port name="OrderWebServicePort" binding="tns:OrderWebServiceBinding">
            <soap:address location="http://localhost:8080/services/OrderWebService"/>
        </port>
    </service>
</definitions>
```

---

## 22. Spring Framework

### История и назначение

**Spring** — это легковесный фреймворк для разработки Java приложений. Создан в 2003 году как альтернатива тяжелым корпоративным решениям.

**Основная задача:** Упростить разработку Java приложений через:

-   Инверсию управления (IoC)
-   Внедрение зависимостей (DI)
-   Аспектно-ориентированное программирование (AOP)

### Сравнение Spring vs Java EE

Характеристика

Spring

Java EE

**Тип**

Фреймворк

Спецификация

**Учебная кривая**

Более крутая

Проще для новичков

**Гибкость**

Высокая

Ограниченная

**Performance**

Хорошая

Очень хорошая

**Экосистема**

Огромная (Spring Boot, Spring Cloud, etc.)

Стандартизированная

**Применение**

Микросервисы, облако

Корпоративные системы

**Контейнер**

Spring Container

Application Server

**Сложность**

Средняя

Может быть сложнее

**Spring более гибкий:**

```java
// Spring: легко подменить реализацию
@Configuration
public class AppConfig {
    @Bean
    public OrderRepository orderRepository() {
        return new JpaOrderRepository();  // или MockOrderRepository
    }
}

// Java EE: нужно использовать CDI qualifiers или конфигурацию
```

**Java EE более стандартизирован:**

```java
// Java EE: стандартная спецификация
@Stateless
public class OrderService { }

// Spring: нет единого способа (разные версии, подходы)
@Service
// или
@Component
// или другие способы
```

### Архитектура Spring

```
Spring Framework
├── Spring Core (IoC, DI)
├── Spring Context
├── Spring AOP
├── Spring DAO/Tx
├── Spring ORM
├── Spring Web (MVC, REST)
├── Spring Security
└── Spring Messaging
    ↓
Spring Boot (стартовая точка с предконфигурацией)
    ↓
Spring Cloud (микросервисы)
```

### Модули Spring

**1. Spring Core (IoC Container)**

-   Основной модуль Spring
-   Управляет beans
-   Выполняет Dependency Injection

```java
@Configuration
public class AppConfig {
    @Bean
    public OrderService orderService() {
        return new OrderService();
    }
    
    @Bean
    public UserRepository userRepository() {
        return new UserRepository();
    }
}

// Использование
public class Main {
    public static void main(String[] args) {
        ApplicationContext context = new AnnotationConfigApplicationContext(AppConfig.class);
        OrderService service = context.getBean(OrderService.class);
    }
}
```

**2. Spring AOP (Aspect-Oriented Programming)**

-   Разделение cross-cutting concerns
-   Логирование, безопасность, транзакции

```java
@Aspect
@Component
public class LoggingAspect {
    
    @Before("execution(* com.example.service.*.*(..))")
    public void logBefore(JoinPoint joinPoint) {
        System.out.println("Calling: " + joinPoint.getSignature());
    }
    
    @After("execution(* com.example.service.*.*(..))")
    public void logAfter(JoinPoint joinPoint) {
        System.out.println("Finished: " + joinPoint.getSignature());
    }
}
```

**3. Spring Data (Data Access)**

-   Упрощает работу с БД
-   JPA, MongoDB, Elasticsearch интеграция

```java
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByUserId(Long userId);
    List<Order> findByOrderDateAfter(LocalDate date);
}

// Использование
@Service
public class OrderService {
    @Autowired
    private OrderRepository orderRepository;
    
    public List<Order> getUserOrders(Long userId) {
        return orderRepository.findByUserId(userId);
    }
}
```

**4. Spring Web (MVC, REST)**

-   Веб-приложения
-   REST контроллеры

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    @Autowired
    private OrderService orderService;
    
    @GetMapping("/{id}")
    public ResponseEntity<Order> getOrder(@PathVariable Long id) {
        Order order = orderService.getOrder(id);
        return ResponseEntity.ok(order);
    }
    
    @PostMapping
    public ResponseEntity<Order> createOrder(@RequestBody Order order) {
        Order created = orderService.createOrder(order);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }
}
```

**5. Spring Security**

-   Аутентификация
-   Авторизация
-   Защита от атак

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            .authorizeRequests()
                .antMatchers("/public/**").permitAll()
                .antMatchers("/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            .and()
            .formLogin()
                .loginPage("/login");
    }
}
```

**6. Spring Messaging**

-   Работа с JMS, Kafka, RabbitMQ
-   Асинхронная обработка

```java
@Component
public class MessageListener {
    
    @JmsListener(destination = "orderQueue")
    public void processOrder(Order order) {
        System.out.println("Processing: " + order);
    }
}
```

### Spring Boot

**Spring Boot** — это расширение Spring, которое упрощает создание standalone приложений.

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

// application.properties
spring.datasource.url=jdbc:mysql://localhost/mydb
spring.datasource.username=root
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
```

**Преимущества Spring Boot:**

-   Минимальная конфигурация
-   Встроенный Tomcat
-   Автоматическая конфигурация
-   Простое добавление зависимостей

---

## 23. Spring Security

### Основные концепции

**1. Authentication (Аутентификация)**

-   Определение кто вы
-   Проверка учетных данных

```java
@Service
public class CustomUserDetailsService implements UserDetailsService {
    
    @Override
    public UserDetails loadUserByUsername(String username) 
            throws UsernameNotFoundException {
        User user = userRepository.findByUsername(username);
        if (user == null) {
            throw new UsernameNotFoundException("User not found");
        }
        
        return new org.springframework.security.core.userdetails.User(
            user.getUsername(),
            user.getPassword(),
            buildAuthorities(user.getRoles())
        );
    }
    
    private Collection<? extends GrantedAuthority> buildAuthorities(
            Set<Role> roles) {
        return roles.stream()
            .map(role -> new SimpleGrantedAuthority("ROLE_" + role.getName()))
            .collect(Collectors.toList());
    }
}
```

**2. Authorization (Авторизация)**

-   Определение что вы можете делать
-   Проверка разрешений

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    @GetMapping
    @PreAuthorize("hasRole('USER')")  // Только авторизованные пользователи
    public List<Order> getOrders() {
        return orderService.getAllOrders();
    }
    
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")  // Только администраторы
    public void deleteOrder(@PathVariable Long id) {
        orderService.deleteOrder(id);
    }
    
    @PostMapping("/{id}/approve")
    @PreAuthorize("hasAuthority('APPROVE_ORDERS')")  // Специфическое разрешение
    public void approveOrder(@PathVariable Long id) {
        orderService.approveOrder(id);
    }
}
```

### Authentication Provider

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    
    @Autowired
    private CustomUserDetailsService userDetailsService;
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
    
    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
        auth
            .userDetailsService(userDetailsService)
            .passwordEncoder(passwordEncoder());
    }
    
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            .authorizeRequests()
                .antMatchers("/public/**").permitAll()
                .antMatchers("/user/**").hasRole("USER")
                .antMatchers("/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            .and()
            .formLogin()
                .loginPage("/login")
                .defaultSuccessUrl("/home")
            .and()
            .logout()
                .logoutUrl("/logout")
                .logoutSuccessUrl("/login");
    }
}
```

---

## 24. Spring Data

### Spring Data JPA

```java
// Entity
@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "total_amount")
    private BigDecimal totalAmount;
    
    @ManyToOne
    @JoinColumn(name = "user_id")
    private User user;
    
    @OneToMany(mappedBy = "order")
    private List<OrderItem> items;
}

// Repository
@Repository
public interface OrderRepository extends JpaRepository<Order, Long>, 
                                        JpaSpecificationExecutor<Order> {
    
    // Query methods (автоматически реализуются)
    List<Order> findByUserId(Long userId);
    List<Order> findByTotalAmountGreaterThan(BigDecimal amount);
    List<Order> findByUserIdOrderByIdDesc(Long userId);
    
    // Custom query
    @Query("SELECT o FROM Order o WHERE o.user.id = ?1")
    List<Order> getOrdersByUser(Long userId);
    
    // Native SQL
    @Query(value = "SELECT * FROM orders WHERE total_amount > ?1", 
           nativeQuery = true)
    List<Order> findExpensiveOrders(BigDecimal amount);
}

// Service
@Service
public class OrderService {
    
    @Autowired
    private OrderRepository orderRepository;
    
    public List<Order> getUserOrders(Long userId) {
        return orderRepository.findByUserId(userId);
    }
    
    @Transactional
    public Order createOrder(Order order) {
        return orderRepository.save(order);
    }
    
    @Transactional
    public void deleteOrder(Long id) {
        orderRepository.deleteById(id);
    }
}
```

### Spring Data Specification

```java
@Service
public class OrderSearchService {
    
    @Autowired
    private OrderRepository orderRepository;
    
    public List<Order> search(String username, BigDecimal minAmount, 
                              BigDecimal maxAmount) {
        Specification<Order> spec = Specification
            .where(byUsername(username))
            .and(byAmountRange(minAmount, maxAmount));
        
        return orderRepository.findAll(spec);
    }
    
    private static Specification<Order> byUsername(String username) {
        return (root, query, cb) -> {
            if (username == null || username.isEmpty()) {
                return null;
            }
            return cb.equal(root.get("user").get("username"), username);
        };
    }
    
    private static Specification<Order> byAmountRange(BigDecimal minAmount, 
                                                      BigDecimal maxAmount) {
        return (root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();
            
            if (minAmount != null) {
                predicates.add(cb.greaterThanOrEqualTo(
                    root.get("totalAmount"), minAmount));
            }
            
            if (maxAmount != null) {
                predicates.add(cb.lessThanOrEqualTo(
                    root.get("totalAmount"), maxAmount));
            }
            
            return cb.and(predicates.toArray(new Predicate[0]));
        };
    }
}
```

### Pagination and Sorting

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    @Autowired
    private OrderRepository orderRepository;
    
    @GetMapping
    public Page<Order> getOrders(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "id") String sortBy,
            @RequestParam(defaultValue = "ASC") Sort.Direction direction) {
        
        Pageable pageable = PageRequest.of(page, size, 
                                          Sort.by(direction, sortBy));
        return orderRepository.findAll(pageable);
    }
}
```

---

## 25. React.js

### Основные принципы

**1. Component-Based**

-   UI состоит из компонентов
-   Переиспользуемые части интерфейса

**2. Virtual DOM**

-   React не обновляет реальный DOM напрямую
-   Вычисляет изменения и применяет их эффективно

**3. Unidirectional Data Flow**

-   Данные передаются от родителя к детям
-   Дети не могут изменять props родителя напрямую

### Архитектура React Application

```
App.jsx (Root)
├── Header
│   ├── Logo
│   └── Navigation
├── MainContent
│   ├── Sidebar
│   └── ProductList
│       ├── Product
│       ├── Product
│       └── Product
└── Footer
```

### Функциональные компоненты

```javascript
// Простой компонент
function Greeting() {
    return <h1>Hello, World!</h1>;
}

// Компонент с JSX
function UserCard({ name, email }) {
    return (
        <div className="card">
            <h2>{name}</h2>
            <p>{email}</p>
        </div>
    );
}

export default UserCard;
```

### State и Props

**Props (свойства)**

-   Передаются от родителя
-   Readonly
-   Используются для конфигурации компонента

```javascript
function Product({ id, name, price }) {
    return (
        <div>
            <h3>{name}</h3>
            <p>Price: ${price}</p>
        </div>
    );
}

// Использование
<Product id={1} name="Laptop" price={999} />
```

**State (состояние)**

-   Локальное состояние компонента
-   Может изменяться
-   Изменение состояния вызывает перерендер

```javascript
import { useState } from 'react';

function Counter() {
    const [count, setCount] = useState(0);
    
    return (
        <div>
            <p>Count: {count}</p>
            <button onClick={() => setCount(count + 1)}>
                Increment
            </button>
        </div>
    );
}
```

### "Умные" (Smart) и "Глупые" (Dumb) компоненты

**Dumb Component (Presentational)**

-   Получает все данные через props
-   Не имеет логики
-   Переиспользуемый

```javascript
function OrderList({ orders, onDelete }) {
    return (
        <div>
            {orders.map(order => (
                <div key={order.id}>
                    <p>{order.name} - ${order.amount}</p>
                    <button onClick={() => onDelete(order.id)}>
                        Delete
                    </button>
                </div>
            ))}
        </div>
    );
}

export default OrderList;
```

**Smart Component (Container)**

-   Содержит логику
-   Управляет состоянием
-   Передает данные в dumb компоненты

```javascript
import { useState, useEffect } from 'react';
import OrderList from './OrderList';

function OrderContainer() {
    const [orders, setOrders] = useState([]);
    
    useEffect(() => {
        // Загрузить заказы с сервера
        fetch('/api/orders')
            .then(res => res.json())
            .then(data => setOrders(data));
    }, []);
    
    const handleDelete = (id) => {
        setOrders(orders.filter(order => order.id !== id));
    };
    
    return <OrderList orders={orders} onDelete={handleDelete} />;
}

export default OrderContainer;
```

### JSX

**JSX** — это синтаксис для описания UI в JavaScript.

```javascript
// JSX компилируется в JavaScript
const element = <h1 className="greeting">Hello</h1>;

// Эквивалентно:
const element = React.createElement(
    'h1',
    { className: 'greeting' },
    'Hello'
);
```

**Основные правила JSX:**

```javascript
// 1. Возвращаем один корневой элемент
function Component() {
    return (
        <div>
            <h1>Title</h1>
            <p>Content</p>
        </div>
    );
}

// 2. Используем className вместо class
<div className="container">Content</div>

// 3. Используем htmlFor вместо for
<label htmlFor="name">Name:</label>
<input id="name" />

// 4. Встраиваем JavaScript выражения
const name = "John";
const element = <h1>Hello, {name}!</h1>;

// 5. Условный рендер
{isLoggedIn ? <Dashboard /> : <Login />}

// 6. Рендер списка
{items.map(item => <Item key={item.id} {...item} />)}

// 7. Props распространение
const props = { name: "John", age: 30 };
<Person {...props} />
```

### Lifecycle методы (Hooks)

**useEffect** — вызывается при монтировании и обновлении

```javascript
import { useEffect } from 'react';

function UserProfile({ userId }) {
    const [user, setUser] = useState(null);
    
    useEffect(() => {
        // Запускается при монтировании и при изменении userId
        fetch(`/api/users/${userId}`)
            .then(res => res.json())
            .then(data => setUser(data));
    }, [userId]);  // Dependency array
    
    useEffect(() => {
        // Запускается при монтировании
        console.log("Component mounted");
        
        return () => {
            // Cleanup function - вызывается при размонтировании
            console.log("Component unmounted");
        };
    }, []);  // Пустой массив = только при монтировании
    
    return <div>{user ? <h1>{user.name}</h1> : <p>Loading...</p>}</div>;
}
```

### React Router

**Навигация между страницами**

```javascript
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

function App() {
    return (
        <BrowserRouter>
            <nav>
                <Link to="/">Home</Link>
                <Link to="/products">Products</Link>
                <Link to="/about">About</Link>
            </nav>
            
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/products" element={<ProductsPage />} />
                <Route path="/products/:id" element={<ProductDetail />} />
                <Route path="/about" element={<AboutPage />} />
                <Route path="*" element={<NotFoundPage />} />
            </Routes>
        </BrowserRouter>
    );
}
```

**Использование параметров из URL**

```javascript
import { useParams } from 'react-router-dom';

function ProductDetail() {
    const { id } = useParams();
    
    const [product, setProduct] = useState(null);
    
    useEffect(() => {
        fetch(`/api/products/${id}`)
            .then(res => res.json())
            .then(data => setProduct(data));
    }, [id]);
    
    return product ? (
        <div>
            <h1>{product.name}</h1>
            <p>${product.price}</p>
        </div>
    ) : (
        <p>Loading...</p>
    );
}
```

---

## 26. Redux (State Management)

**Redux** — это библиотека для управления состоянием приложения.

### Основные концепции

**1. Store**

-   Центральное хранилище состояния
-   Единственный источник истины

**2. Action**

-   Объект, который описывает что произошло
-   Содержит type и payload

**3. Reducer**

-   Чистая функция, которая обновляет state
-   (state, action) => newState

**4. Dispatch**

-   Способ отправить action в store

### Простой пример Redux

```javascript
import { createStore } from 'redux';

// 1. Initial state
const initialState = {
    count: 0
};

// 2. Action types
const INCREMENT = 'INCREMENT';
const DECREMENT = 'DECREMENT';

// 3. Actions
const increment = () => ({ type: INCREMENT });
const decrement = () => ({ type: DECREMENT });

// 4. Reducer
function counterReducer(state = initialState, action) {
    switch (action.type) {
        case INCREMENT:
            return { ...state, count: state.count + 1 };
        case DECREMENT:
            return { ...state, count: state.count - 1 };
        default:
            return state;
    }
}

// 5. Store
const store = createStore(counterReducer);

// 6. Использование
store.dispatch(increment());
store.dispatch(increment());
console.log(store.getState());  // { count: 2 }

store.dispatch(decrement());
console.log(store.getState());  // { count: 1 }
```

### Redux с React

```javascript
import { useSelector, useDispatch } from 'react-redux';

function Counter() {
    const count = useSelector(state => state.counter.count);
    const dispatch = useDispatch();
    
    return (
        <div>
            <p>Count: {count}</p>
            <button onClick={() => dispatch(increment())}>+</button>
            <button onClick={() => dispatch(decrement())}>-</button>
        </div>
    );
}

// Wrapping app with Provider
import { Provider } from 'react-redux';

function App() {
    return (
        <Provider store={store}>
            <Counter />
        </Provider>
    );
}
```

### Redux Async Actions (Middleware)

```javascript
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

// Async action
export const fetchOrders = createAsyncThunk(
    'orders/fetchOrders',
    async (userId) => {
        const response = await fetch(`/api/users/${userId}/orders`);
        return response.json();
    }
);

// Slice (современный подход)
const ordersSlice = createSlice({
    name: 'orders',
    initialState: {
        items: [],
        loading: false,
        error: null
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchOrders.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchOrders.fulfilled, (state, action) => {
                state.loading = false;
                state.items = action.payload;
            })
            .addCase(fetchOrders.rejected, (state, action) => {
                state.loading = false;
                state.error = action.error.message;
            });
    }
});

export default ordersSlice.reducer;
```

---

## 27. Angular Framework

### Архитектура Angular

```
Angular Application
├── Modules
│   ├── AppModule
│   ├── OrdersModule
│   └── SharedModule
├── Components
│   ├── AppComponent
│   ├── OrderList
│   └── OrderDetail
├── Services
│   ├── OrderService
│   └── UserService
├── Models
│   ├── Order
│   └── User
├── Routing
└── Dependency Injection
```

### Модули (NgModules)

```typescript
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { OrderListComponent } from './components/order-list/order-list.component';
import { OrderService } from './services/order.service';

@NgModule({
  declarations: [
    AppComponent,
    OrderListComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule
  ],
  providers: [OrderService],  // Dependency Injection
  bootstrap: [AppComponent]
})
export class AppModule { }
```

### Компоненты

```typescript
import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { Order } from '../../models/order.model';

@Component({
  selector: 'app-order-list',
  templateUrl: './order-list.component.html',
  styleUrls: ['./order-list.component.css']
})
export class OrderListComponent implements OnInit {
  
  @Input()
  orders: Order[] = [];
  
  @Output()
  orderSelected = new EventEmitter<Order>();
  
  @Output()
  orderDeleted = new EventEmitter<Long>();
  
  selectedOrder: Order | null = null;
  
  constructor() { }
  
  ngOnInit(): void {
    // Инициализация компонента
  }
  
  selectOrder(order: Order): void {
    this.selectedOrder = order;
    this.orderSelected.emit(order);
  }
  
  deleteOrder(id: number): void {
    this.orderDeleted.emit(id);
  }
}
```

**Template (order-list.component.html):**

```html
<div class="order-list">
  <div *ngFor="let order of orders" 
       [class.selected]="order === selectedOrder"
       (click)="selectOrder(order)">
    <h3>{{ order.id }}</h3>
    <p>Amount: ${{ order.amount }}</p>
    <button (click)="deleteOrder(order.id)">Delete</button>
  </div>
</div>
```

### Services и Dependency Injection

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Order } from '../models/order.model';

@Injectable({
  providedIn: 'root'  // Singleton
})
export class OrderService {
  
  private apiUrl = '/api/orders';
  
  constructor(private http: HttpClient) { }
  
  getOrders(): Observable<Order[]> {
    return this.http.get<Order[]>(this.apiUrl);
  }
  
  getOrder(id: number): Observable<Order> {
    return this.http.get<Order>(`${this.apiUrl}/${id}`);
  }
  
  createOrder(order: Order): Observable<Order> {
    return this.http.post<Order>(this.apiUrl, order);
  }
  
  updateOrder(id: number, order: Order): Observable<void> {
    return this.http.put<void>(`${this.apiUrl}/${id}`, order);
  }
  
  deleteOrder(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
```

**Использование Service в Component:**

```typescript
@Component({
  selector: 'app-order-container',
  template: `<app-order-list [orders]="orders"></app-order-list>`
})
export class OrderContainerComponent implements OnInit {
  
  orders: Order[] = [];
  
  constructor(private orderService: OrderService) { }
  
  ngOnInit(): void {
    this.orderService.getOrders().subscribe(
      (data) => {
        this.orders = data;
      },
      (error) => {
        console.error('Error loading orders:', error);
      }
    );
  }
}
```

### Жизненный цикл компонента (Lifecycle Hooks)

```typescript
import { Component, OnInit, OnDestroy, OnChanges, SimpleChanges } from '@angular/core';

@Component({
  selector: 'app-example',
  template: '<p>Example</p>'
})
export class ExampleComponent implements OnInit, OnDestroy, OnChanges {
  
  @Input()
  data: any;
  
  // 1. Constructor
  constructor() {
    console.log('1. Constructor');
  }
  
  // 2. OnChanges
  ngOnChanges(changes: SimpleChanges): void {
    console.log('2. OnChanges', changes);
  }
  
  // 3. OnInit
  ngOnInit(): void {
    console.log('3. OnInit - инициализация');
  }
  
  // 4. DoCheck
  ngDoCheck(): void {
    console.log('4. DoCheck - проверка изменений');
  }
  
  // 5. AfterContentInit
  ngAfterContentInit(): void {
    console.log('5. AfterContentInit');
  }
  
  // 6. AfterViewInit
  ngAfterViewInit(): void {
    console.log('6. AfterViewInit');
  }
  
  // 7. OnDestroy
  ngOnDestroy(): void {
    console.log('7. OnDestroy - очистка ресурсов');
  }
}
```

**Порядок вызова:**

```
1. Constructor → создание компонента
2. ngOnChanges → изменение @Input
3. ngOnInit → инициализация
4. ngDoCheck → проверка изменений
5. ngAfterContentInit → инициализация содержимого
6. ngAfterViewInit → инициализация представления
7. ngOnDestroy → удаление компонента
```

### Шаблоны (Templates)

**Интерполяция:**

```html
<p>{{ message }}</p>
<p>{{ 1 + 1 }}</p>
<p>{{ getName() }}</p>
```

**Property binding:**

```html
<img [src]="imageUrl">
<input [disabled]="isDisabled">
<div [style.background-color]="backgroundColor"></div>
<div [class.highlight]="isHighlighted"></div>
```

**Event binding:**

```html
<button (click)="handleClick()">Click me</button>
<input (keyup)="onKeyUp($event)">
<form (submit)="submitForm()"></form>
```

**Two-way binding:**

```html
<input [(ngModel)]="username">
<!-- Эквивалентно: -->
<input [ngModel]="username" (ngModelChange)="username = $event">
```

**Директивы:**

```html
<!-- Условный рендер -->
<div *ngIf="isLoggedIn">Welcome!</div>

<!-- Рендер списка -->
<ul>
  <li *ngFor="let order of orders">{{ order.id }}</li>
</ul>

<!-- Switch -->
<div [ngSwitch]="role">
  <p *ngSwitchCase="'admin'">Admin panel</p>
  <p *ngSwitchCase="'user'">User page</p>
  <p *ngSwitchDefault>Guest</p>
</div>

<!-- ngClass -->
<div [ngClass]="{ 'highlight': isActive, 'large': isLarge }"></div>

<!-- ngStyle -->
<div [ngStyle]="{ 'color': color, 'font-size': fontSize + 'px' }"></div>
```

### Routing

```typescript
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { HomeComponent } from './pages/home/home.component';
import { OrdersComponent } from './pages/orders/orders.component';
import { OrderDetailComponent } from './pages/order-detail/order-detail.component';
import { NotFoundComponent } from './pages/not-found/not-found.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'orders', component: OrdersComponent },
  { path: 'orders/:id', component: OrderDetailComponent },
  { path: '**', component: NotFoundComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
```

**Использование в component:**

```typescript
import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-navigation',
  template: `
    <nav>
      <a routerLink="/">Home</a>
      <a routerLink="/orders">Orders</a>
      <a [routerLink]="['/orders', orderId]">Order Detail</a>
    </nav>
  `
})
export class NavigationComponent {
  orderId = 123;
  
  constructor(private router: Router) { }
  
  navigateToOrders() {
    this.router.navigate(['/orders']);
  }
}
```

### Формы (Template-driven vs Reactive)

**Template-driven Forms:**

```typescript
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-login-form',
  template: `
    <form (ngSubmit)="login()">
      <input [(ngModel)]="username" name="username" required>
      <input [(ngModel)]="password" name="password" type="password" required>
      <button type="submit">Login</button>
    </form>
  `
})
export class LoginFormComponent {
  username = '';
  password = '';
  
  login() {
    console.log('Logging in:', this.username);
  }
}
```

**Reactive Forms:**

```typescript
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-order-form',
  template: `
    <form [formGroup]="form" (ngSubmit)="submitForm()">
      <input formControlName="productName" required>
      <span *ngIf="form.get('productName')?.hasError('required')">
        Required
      </span>
      
      <input formControlName="quantity" type="number" required>
      <input formControlName="price" type="number" required>
      
      <button type="submit" [disabled]="!form.valid">
        Create Order
      </button>
    </form>
  `
})
export class OrderFormComponent implements OnInit {
  form: FormGroup;
  
  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({
      productName: ['', Validators.required],
      quantity: ['', [Validators.required, Validators.min(1)]],
      price: ['', [Validators.required, Validators.min(0)]]
    });
  }
  
  ngOnInit(): void {
  }
  
  submitForm() {
    if (this.form.valid) {
      console.log('Order:', this.form.value);
    }
  }
}
```

### HTTP клиент

```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  
  private apiUrl = '/api';
  
  constructor(private http: HttpClient) { }
  
  // GET запрос
  get<T>(endpoint: string, params?: any): Observable<T> {
    let httpParams = new HttpParams();
    
    if (params) {
      Object.keys(params).forEach(key => {
        httpParams = httpParams.set(key, params[key]);
      });
    }
    
    return this.http.get<T>(
      `${this.apiUrl}/${endpoint}`,
      { params: httpParams }
    ).pipe(
      catchError(this.handleError)
    );
  }
  
  // POST запрос
  post<T>(endpoint: string, data: any): Observable<T> {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    
    return this.http.post<T>(
      `${this.apiUrl}/${endpoint}`,
      data,
      { headers }
    ).pipe(
      catchError(this.handleError)
    );
  }
  
  // PUT запрос
  put<T>(endpoint: string, data: any): Observable<T> {
    return this.http.put<T>(
      `${this.apiUrl}/${endpoint}`,
      data
    ).pipe(
      catchError(this.handleError)
    );
  }
  
  // DELETE запрос
  delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<T>(
      `${this.apiUrl}/${endpoint}`
    ).pipe(
      catchError(this.handleError)
    );
  }
  
  private handleError(error: any) {
    console.error('API error:', error);
    return throwError(() => error);
  }
}
```

---

## Заключение

Этот документ охватывает основные концепции и практические примеры для всех основных технологий в вашем стеке. Ключевые моменты:

### Java EE

-   **Спецификация**, а не реализация
-   CDI для управления зависимостями
-   EJB для бизнес-логики
-   JMS для асинхронной обработки
-   JPA для работы с БД

### Spring

-   **Фреймворк** с большей гибкостью
-   Spring Boot упрощает конфигурацию
-   Модульная архитектура (Security, Data, Web, etc.)

### Frontend

-   **React**: компоненты, JSX, Redux для состояния
-   **Angular**: полнофункциональный фреймворк с модулями, сервисами, DI

Используйте эту информацию для глубокого понимания архитектуры и взаимодействия всех компонентов вашего приложения.