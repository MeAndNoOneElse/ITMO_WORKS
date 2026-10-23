param([string]$CubeIdeRoot = 'C:\ST\STM32CubeIDE_1.19.0\STM32CubeIDE')
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$compiler = Get-ChildItem -LiteralPath (Join-Path $CubeIdeRoot 'plugins') -Filter arm-none-eabi-gcc.exe -Recurse | Select-Object -First 1
if (!$compiler) { throw 'ARM GCC not found. Pass -CubeIdeRoot with your STM32CubeIDE directory.' }
$toolDir = $compiler.DirectoryName
$output = Join-Path $projectRoot 'BuildSnake'
New-Item -ItemType Directory -Force -Path $output | Out-Null
$includes = @('Core/Inc','Drivers/STM32F4xx_HAL_Driver/Inc','Drivers/STM32F4xx_HAL_Driver/Inc/Legacy',
    'Drivers/CMSIS/Device/ST/STM32F4xx/Include','Drivers/CMSIS/Include',
    'Middlewares/Third_Party/FreeRTOS/Source/include','Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS',
    'Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM4F')
$flags = @('-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard',
    '-std=gnu11','-g3','-Og','-DDEBUG','-DUSE_HAL_DRIVER','-DSTM32F427xx',
    '-ffunction-sections','-fdata-sections','-Wall','-Wextra','-fstack-usage','--specs=nano.specs')
foreach ($inc in $includes) { $flags += '-I' + (Join-Path $projectRoot $inc) }
$sourceDirs = @('Core/Src','Drivers/STM32F4xx_HAL_Driver/Src','Middlewares/Third_Party/FreeRTOS/Source',
    'Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS','Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM4F',
    'Middlewares/Third_Party/FreeRTOS/Source/portable/MemMang')
$objects = @()
foreach ($dir in $sourceDirs) {
    foreach ($src in Get-ChildItem -LiteralPath (Join-Path $projectRoot $dir) -Filter '*.c') {
        $obj = Join-Path $output ($src.BaseName + '.o')
        & $compiler.FullName @flags -c $src.FullName -o $obj
        if ($LASTEXITCODE) { throw "Compile failed: $($src.Name)" }
        $objects += $obj
    }
}
$startup = Join-Path $projectRoot 'Core/Startup/startup_stm32f427vitx.s'
$startupObj = Join-Path $output 'startup.o'
& $compiler.FullName @flags -x assembler-with-cpp -c $startup -o $startupObj
if ($LASTEXITCODE) { throw 'Startup assembly failed' }
$objects += $startupObj
$elf = Join-Path $output 'snake.elf'
& $compiler.FullName @objects -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard `
    ('-T' + (Join-Path $projectRoot 'STM32F427VITX_FLASH.ld')) --specs=nosys.specs --specs=nano.specs `
    '-Wl,--gc-sections' ('-Wl,-Map=' + (Join-Path $output 'snake.map')) '-Wl,--start-group' -lc -lm '-Wl,--end-group' -o $elf
if ($LASTEXITCODE) { throw 'Link failed' }
& (Join-Path $toolDir 'arm-none-eabi-objcopy.exe') -O ihex $elf (Join-Path $output 'snake.hex')
if ($LASTEXITCODE) { throw 'HEX generation failed' }
& (Join-Path $toolDir 'arm-none-eabi-objcopy.exe') -O binary $elf (Join-Path $output 'snake.bin')
if ($LASTEXITCODE) { throw 'BIN generation failed' }
& (Join-Path $toolDir 'arm-none-eabi-size.exe') $elf
Write-Host "Firmware ready: $elf"
