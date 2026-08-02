@echo off
docker stop my-wildfly-container
docker rm my-wildfly-container
rmdir /S /Q "C:\Users\Eternal Core\OneDrive - MSFT\github_file\lab_3.4\build"
call gradle clean war
docker-compose up -d
docker build -t my-wildfly-app .
docker run -d -p 8080:8080 -p 9990:9990 --name my-wildfly-container my-wildfly-app

