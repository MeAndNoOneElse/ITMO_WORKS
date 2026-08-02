package com.weblab.db;

import jakarta.persistence.EntityManager;
import jakarta.persistence.EntityManagerFactory;
import jakarta.persistence.Persistence;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

/**
 * Синглтон EntityManagerFactory для Derby + JPA (EclipseLink).
 * БД хранится в ~/.weblab_derby/weblab — файлы сохраняются между запусками.
 */
public class Database {

    private static final EntityManagerFactory EMF;

    static {
        try {
            // Гарантируем существование директории
            java.nio.file.Path dir = Paths.get(System.getProperty("user.home"), ".weblab_derby");
            Files.createDirectories(dir);

            String dbUrl = "jdbc:derby:" + dir.resolve("weblab").toString().replace("\\", "/") + ";create=true";
            System.out.println("[DB] Derby URL: " + dbUrl);

            // Переопределяем URL из persistence.xml (там используется ${user.home}, что не все JPA-провайдеры раскрывают)
            Map<String, String> props = new HashMap<>();
            props.put("jakarta.persistence.jdbc.url", dbUrl);

            EMF = Persistence.createEntityManagerFactory("weblabPU", props);
            System.out.println("[DB] JPA EntityManagerFactory создан (Derby)");
        } catch (Exception e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    public static EntityManager createEntityManager() {
        return EMF.createEntityManager();
    }

    public static EntityManagerFactory getEMF() {
        return EMF;
    }

    /** Вызвать при shutdown сервера */
    public static void close() {
        if (EMF != null && EMF.isOpen()) {
            EMF.close();
            // Graceful Derby shutdown
            try {
                java.sql.DriverManager.getConnection("jdbc:derby:;shutdown=true");
            } catch (Exception ignored) { /* Derby всегда кидает исключение при shutdown */ }
        }
    }

    // Оставляем совместимость (init теперь ничего не делает — схема создаётся JPA)
    public static void init() {
        // JPA сам создаёт схему через schema-generation в persistence.xml
        System.out.println("[DB] Схема создана JPA (Derby)");
    }
}
