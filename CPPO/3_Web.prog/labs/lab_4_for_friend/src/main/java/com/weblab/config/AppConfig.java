package com.weblab.config;

import com.weblab.filter.AuthFilter;
import org.glassfish.jersey.server.ResourceConfig;

/**
 * Конфигурация Jersey приложения — регистрируем пакеты с ресурсами.
 */
public class AppConfig extends ResourceConfig {

    public AppConfig() {
        // Сканируем все классы в пакете com.weblab
        packages("com.weblab.resource", "com.weblab.config", "com.weblab.filter");
        register(JacksonConfig.class);
    }
}

