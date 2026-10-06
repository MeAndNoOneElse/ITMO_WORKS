package com.weblab;

import com.weblab.config.AppConfig;
import com.weblab.db.Database;
import org.glassfish.grizzly.http.server.HttpServer;
import org.glassfish.jersey.grizzly2.httpserver.GrizzlyHttpServerFactory;
import org.glassfish.jersey.server.ResourceConfig;

import java.net.URI;

public class Main {

    public static final String BASE_URI = "http://0.0.0.0:8080/";

    public static void main(String[] args) throws Exception {
        // Инициализация JPA + Derby (схема создаётся автоматически)
        Database.init();

        ResourceConfig config = new AppConfig();
        HttpServer server = GrizzlyHttpServerFactory.createHttpServer(URI.create(BASE_URI), config);

        // Корректно закрываем Derby при остановке
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            server.shutdownNow();
            Database.close();
            System.out.println("[DB] Derby остановлена.");
        }));

        System.out.println("===========================================");
        System.out.println("  JAX-RS Server запущен на порту 8080");
        System.out.println("  http://localhost:8080/api/");
        System.out.println("  Нажмите ENTER для остановки...");
        System.out.println("===========================================");

        System.in.read();
        server.shutdownNow();
        Database.close();
    }
}
