param([string]$Compiler = 'C:\Program Files\JetBrains\CLion 2025.2.1\bin\mingw\bin\gcc.exe')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$previousPath = $env:PATH
$env:PATH = (Split-Path $Compiler -Parent) + ';' + $env:PATH
Push-Location $projectRoot
try {
    & $Compiler -std=c11 -Wall -Wextra -Werror -ICore/Inc Core/Src/snake.c Core/Src/game_view.c tests/test_snake.c -o tests/test_snake.exe
    if ($LASTEXITCODE) { throw 'Test compilation failed' }
    & ./tests/test_snake.exe
    if ($LASTEXITCODE) { throw 'Tests failed' }
} finally { Pop-Location; $env:PATH = $previousPath }
