@echo off
setlocal enabledelayedexpansion

rem --- Параметры ---
set TEAM_BUILD_DIR=%1
set TEAM_JARS_DIR=%2
set ZIP_NAME=%3
set APP_NAME=%4
set NUM_REVISIONS=4

echo "Team build started..."
echo "Build directory: %TEAM_BUILD_DIR%"
echo "Jars directory: %TEAM_JARS_DIR%"
echo "ZIP file name: %ZIP_NAME%"
echo "App name: %APP_NAME%"

rem --- Получение последних коммитов ---
git log -%NUM_REVISIONS% --pretty=format:"%%H" > "%TEAM_BUILD_DIR%\revisions.txt"

if %ERRORLEVEL% neq 0 (
    echo "Failed to get Git revisions."
    exit /b 1
)

echo "Found revisions:"
type "%TEAM_BUILD_DIR%\revisions.txt"

rem --- Сборка каждой ревизии ---
for /f "tokens=*" %%r in (%TEAM_BUILD_DIR%\revisions.txt) do (
    set "REVISION=%%r"
    set "REVISION_SHORT=!REVISION:~0,7!"
    set "BUILD_SUBDIR=%TEAM_BUILD_DIR%\!REVISION_SHORT!"
    set "JAR_NAME=%APP_NAME%-!REVISION_SHORT!.jar"

    echo "--- Building revision !REVISION_SHORT! ---"

    rem --- Создание временной директории для сборки ---
    mkdir "!BUILD_SUBDIR!"
    git checkout-index -a -f --prefix="!BUILD_SUBDIR!\\"
    if %ERRORLEVEL% neq 0 (
        echo "Failed to checkout revision !REVISION_SHORT!."
        continue
    )

    rem --- Запуск сборки Ant ---
    echo "Running Ant build for !REVISION_SHORT!..."
    ant -Dbuild.dir="!BUILD_SUBDIR!\build" -Djar.name="!JAR_NAME!" build
    if %ERRORLEVEL% neq 0 (
        echo "Ant build failed for revision !REVISION_SHORT!."
        continue
    )

    rem --- Копирование JAR-файла ---
    copy "!BUILD_SUBDIR!\build\jar\!JAR_NAME!" "%TEAM_JARS_DIR%\"
    if %ERRORLEVEL% neq 0 (
        echo "Failed to copy JAR for revision !REVISION_SHORT!."
    )
)

rem --- Упаковка в ZIP-архив ---
echo "--- Creating ZIP archive ---"
jar -c -f "%ZIP_NAME%" -C "%TEAM_JARS_DIR%" .
if %ERRORLEVEL% neq 0 (
    echo "Failed to create ZIP archive."
    exit /b 1
)

echo "Team build finished successfully. ZIP archive created at %ZIP_NAME%"
endlocal
