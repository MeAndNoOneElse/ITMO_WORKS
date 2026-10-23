from pathlib import Path
import re, shutil
root = Path.cwd()
backup = root / 'backup_before_snake'
backup.mkdir(exist_ok=True)
for name in ['Core/Src/main.c','Core/Src/freertos.c','Core/Src/stm32f4xx_hal_msp.c','Core/Inc/FreeRTOSConfig.h','Core/Inc/stm32f4xx_hal_conf.h','tetris.ioc']:
    dest = backup / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists(): shutil.copy2(root / name, dest)
def section(s, name, content):
    return re.sub(r'(/\* USER CODE BEGIN '+re.escape(name)+r' \*/).*?(/\* USER CODE END '+re.escape(name)+r' \*/)', lambda m:m[1]+'\n'+content+'\n'+m[2], s, flags=re.S)
p = root/'Core/Src/main.c'
s = p.read_text()
s = section(s, 'Includes', '#include "app_game.h"\n#include "board_game.h"')
s = s.replace('osThreadId defaultTaskHandle;', 'I2C_HandleTypeDef hi2c1;\nosThreadId displayTaskHandle;\nosThreadId defaultTaskHandle;')
s = s.replace('static void MX_GPIO_Init(void);', 'static void MX_GPIO_Init(void);\nstatic void MX_I2C1_Init(void);\nvoid StartDisplayTask(void const *argument);')
s = s.replace('  MX_GPIO_Init();', '  MX_GPIO_Init();\n  MX_I2C1_Init();')
s = section(s, '2', '  Board_Init();')
s = section(s, 'RTOS_MUTEX', '  App_Init();')
s = s.replace('StartDefaultTask, osPriorityNormal, 0, 128', 'StartDefaultTask, osPriorityAboveNormal, 0, 384')
s = s.replace('StartTask02, osPriorityIdle, 0, 128', 'StartTask02, osPriorityNormal, 0, 512')
s = s.replace('  /* USER CODE BEGIN RTOS_THREADS */', '  osThreadDef(displayTask, StartDisplayTask, osPriorityBelowNormal, 0, 512);\n  displayTaskHandle = osThreadCreate(osThread(displayTask), NULL);\n\n  /* USER CODE BEGIN RTOS_THREADS */')
s = section(s, 'RTOS_THREADS', '  if (!defaultTaskHandle || !myTask02Handle || !displayTaskHandle) Error_Handler();')
s = section(s, '5', '  App_InputTask(argument);')
s = section(s, 'StartTask02', '  App_GameTask(argument);')
s = s.replace('/**\n  * @brief  Period elapsed callback', '''/* USER CODE BEGIN Header_StartDisplayTask */
/* OLED owner task. */
/* USER CODE END Header_StartDisplayTask */
void StartDisplayTask(void const *argument)
{
  /* USER CODE BEGIN StartDisplayTask */
  App_DisplayTask(argument);
  /* USER CODE END StartDisplayTask */
}

/**
  * @brief  Period elapsed callback''')
s = s.replace('/**\n  * @brief GPIO Initialization Function', '''static void MX_I2C1_Init(void)
{
  hi2c1.Instance = I2C1;
  hi2c1.Init.ClockSpeed = 100000;
  hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK) Error_Handler();
}

/**
  * @brief GPIO Initialization Function''')
s = section(s, 'Error_Handler_Debug', '''  __HAL_RCC_GPIOD_CLK_ENABLE();
  GPIOD->BSRR = GPIO_PIN_14 | ((uint32_t)(GPIO_PIN_13 | GPIO_PIN_15) << 16);
  __disable_irq();
  while (1) { }''')
p.write_text(s)
p = root/'Core/Src/stm32f4xx_hal_msp.c'
s=p.read_text()
s += '''
void HAL_I2C_MspInit(I2C_HandleTypeDef *hi2c)
{
  if (hi2c->Instance == I2C1) {
    GPIO_InitTypeDef gpio = {0};
    __HAL_RCC_GPIOB_CLK_ENABLE();
    gpio.Pin = GPIO_PIN_8 | GPIO_PIN_9;
    gpio.Mode = GPIO_MODE_AF_OD;
    gpio.Pull = GPIO_PULLUP;
    gpio.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    gpio.Alternate = GPIO_AF4_I2C1;
    HAL_GPIO_Init(GPIOB, &gpio);
    __HAL_RCC_I2C1_CLK_ENABLE();
  }
}
'''
p.write_text(s)
p = root/'Core/Inc/stm32f4xx_hal_conf.h'
s=p.read_text().replace('/* #define HAL_I2C_MODULE_ENABLED */','#define HAL_I2C_MODULE_ENABLED')
p.write_text(s)
source = Path('C:/Users/Asus/STM32Cube/Repository/STM32Cube_FW_F4_V1.28.2/Drivers/STM32F4xx_HAL_Driver')
for sub, name in [('Src','stm32f4xx_hal_i2c.c'),('Src','stm32f4xx_hal_i2c_ex.c'),('Inc','stm32f4xx_hal_i2c.h'),('Inc','stm32f4xx_hal_i2c_ex.h')]:
    shutil.copy2(source/sub/name, root/'Drivers/STM32F4xx_HAL_Driver'/sub/name)
p=root/'Core/Inc/FreeRTOSConfig.h'
s=p.read_text().replace('INCLUDE_vTaskDelayUntil              0','INCLUDE_vTaskDelayUntil              1')
s=section(s,'Defines', '''#define configUSE_TIME_SLICING 1
#define configCHECK_FOR_STACK_OVERFLOW 2
#define configUSE_MALLOC_FAILED_HOOK 1''')
p.write_text(s)
p=root/'Core/Src/freertos.c'
s=section(p.read_text(),'Application','''void vApplicationStackOverflowHook(TaskHandle_t task, char *name)
{
  (void)task; (void)name;
  Error_Handler();
}
void vApplicationMallocFailedHook(void)
{
  Error_Handler();
}''')
p.write_text(s)
p=root/'tetris.ioc'
s=p.read_text()
s=re.sub(r'FREERTOS.Tasks01=.*', 'FREERTOS.Tasks01=defaultTask,1,384,StartDefaultTask,Default,NULL,Dynamic,NULL,NULL;myTask02,0,512,StartTask02,Default,NULL,Dynamic,NULL,NULL;displayTask,-1,512,StartDisplayTask,Default,NULL,Dynamic,NULL,NULL', s)
s=s.replace('FREERTOS.IPParameters=Tasks01,FootprintOK','FREERTOS.IPParameters=Tasks01,FootprintOK,INCLUDE_vTaskDelayUntil')
s += '\nFREERTOS.INCLUDE_vTaskDelayUntil=1\n'
s=s.replace('Mcu.IPNb=4','Mcu.IP4=I2C1\nMcu.IPNb=5')
s=s.replace('Mcu.PinsNb=10','Mcu.Pin10=PB8\nMcu.Pin11=PB9\nMcu.PinsNb=12')
s+='''I2C1.ClockSpeed=100000
I2C1.IPParameters=ClockSpeed
PB8.Mode=I2C
PB8.Signal=I2C1_SCL
PB8.GPIOParameters=GPIO_PuPd
PB8.GPIO_PuPd=GPIO_PULLUP
PB9.Mode=I2C
PB9.Signal=I2C1_SDA
PB9.GPIOParameters=GPIO_PuPd
PB9.GPIO_PuPd=GPIO_PULLUP
'''
s=s.replace('ProjectManager.functionlistsort=1-SystemClock_Config-RCC-false-HAL-false','ProjectManager.functionlistsort=1-SystemClock_Config-RCC-false-HAL-false,2-MX_GPIO_Init-GPIO-false-HAL-true,3-MX_I2C1_Init-I2C1-false-HAL-true')
p.write_text(s)
