FROM quay.io/wildfly/wildfly:35.0.0.Final-jdk17



# Копируем ваш WAR файл в директорию развертывания WildFly
COPY build/libs/lab_3.4.war /opt/jboss/wildfly/standalone/deployments/

# Открываем порт WildFly
EXPOSE 8080

# Запускаем WildFly, биндим на все интерфейсы для доступа из контейнера
CMD ["/opt/jboss/wildfly/bin/standalone.sh", "-b", "0.0.0.0"]