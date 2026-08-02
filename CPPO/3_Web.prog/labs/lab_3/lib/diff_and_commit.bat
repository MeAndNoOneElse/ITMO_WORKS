@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "EXCLUDE_LIST=%~1"
set "EXCLUDE_LIST=%EXCLUDE_LIST: =%"
set "COMMIT_MSG=%~2"
if not defined COMMIT_MSG set "COMMIT_MSG=Auto-commit from Ant"

pushd "%~dp0\.."

echo Getting SVN status...
svn status > "%TEMP%\svn_status.txt" 2>nul
if errorlevel 1 (
    echo SVN status failed.
    popd
    exit /b 1
)

type "%TEMP%\svn_status.txt"

set "BLOCK=0"
for /f "usebackq tokens=1,* delims= " %%A in ("%TEMP%\svn_status.txt") do (
    set "FILE=%%B"
    for %%F in ("!FILE!") do (
        set "FILENAME=%%~nF"
        if /I "%%~xF"==".java" (
            set "MATCH=0"
            echo ,!EXCLUDE_LIST!, | findstr /I /C:",!FILENAME!," >nul
            if not errorlevel 1 set "MATCH=1"

            if "!MATCH!"=="1" (
                echo Found excluded class: !FILENAME!
                set "BLOCK=1"
            )
        )
    )
)

if "%BLOCK%"=="1" (
    echo Commit skipped: modified files intersect with excluded class list.
    popd
    exit /b 0
)

echo Performing SVN commit...
svn add --force . >nul 2>&1
svn commit -m "%COMMIT_MSG%"

popd
exit /b %errorlevel%
