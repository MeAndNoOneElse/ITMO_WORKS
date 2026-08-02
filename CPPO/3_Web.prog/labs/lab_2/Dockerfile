FROM quay.io/wildfly/wildfly:latest

# Копируем WAR-файл в директорию деплоя WildFly
COPY ./build/libs/app.war /opt/jboss/wildfly/standalone/deployments/

# Открываем порты для всех IP
CMD ["/opt/jboss/wildfly/bin/standalone.sh", "-b", "0.0.0.0", "-bmanagement", "0.0.0.0"]
