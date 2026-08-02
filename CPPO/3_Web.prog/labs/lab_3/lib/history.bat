@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "WORKDIR=%~1"
if "!WORKDIR!"=="." set "WORKDIR=%CD%"
if not defined WORKDIR set "WORKDIR=%~dp0\.."

echo Working directory: !WORKDIR!
pushd "!WORKDIR!"

echo Determining current SVN revision...
for /f "delims=" %%R in ('svn info --show-item revision 2^>nul') do set "CUR_REV=%%R"
if not defined CUR_REV (
    echo Cannot determine current SVN revision.
    popd
    exit /b 1
)

echo Current revision: !CUR_REV!

set "TRY_REV=!CUR_REV!"
set "LAST_GOOD="
set "NEXT_REV="

:loop
if !TRY_REV! LEQ 1 goto finish

set /a PREV_REV=!TRY_REV!-1
echo Trying revision !PREV_REV!...
svn update -r !PREV_REV! >nul 2>&1
if errorlevel 1 (
    echo SVN update failed for revision !PREV_REV!.
    set "TRY_REV=!PREV_REV!"
    goto loop
)

echo Testing compilation...
call ant -f "!WORKDIR!\build.xml" clean compile 2>nul
if not errorlevel 1 (
    echo Revision !PREV_REV! compiled successfully!
    set "LAST_GOOD=!PREV_REV!"
    set "NEXT_REV=!TRY_REV!"
    goto finish
)

echo Revision !PREV_REV! failed to compile.
set "TRY_REV=!PREV_REV!"
goto loop

:finish
if defined LAST_GOOD (
    echo Last good revision: !LAST_GOOD!
    echo Next revision: !NEXT_REV!
    set "DIFF_FILE=!WORKDIR!\history_diff_r!LAST_GOOD!_r!NEXT_REV!.diff"
    echo Generating diff...
    svn diff -r !LAST_GOOD!:!NEXT_REV! > "!DIFF_FILE!"
    echo Diff saved to !DIFF_FILE!
) else (
    echo No working revision found.
)

echo Returning to HEAD...
svn update -r HEAD >nul 2>&1
popd
exit /b 0

