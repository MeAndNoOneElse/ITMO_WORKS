/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * File Name          : freertos.c
  * Description        : Code for freertos applications
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "FreeRTOS.h"
#include "task.h"
#include "main.h"
#include "cmsis_os.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "usart.h"
#include <string.h>
#include <stdio.h>

#include "snake.h"
#include "oled.h"
#include "fonts.h"
#include "sdk_uart.h"
#include "kb.h"
#include "pca9538.h"
#include "i2c.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */
/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
/* USER CODE BEGIN Variables */
/* USER CODE END Variables */
osThreadId keypadTaskHandle;
osThreadId gameTaskHandle;
osMessageQId inputQueueHandle;
osMutexId I2CMutexHandle;

/* Private function prototypes -----------------------------------------------*/
/* USER CODE BEGIN FunctionPrototypes */

/* USER CODE END FunctionPrototypes */

void StartKeypadTask(void const * argument);
void StartGameTask(void const * argument);

void MX_FREERTOS_Init(void); /* (MISRA C 2004 rule 8.1) */

/* GetIdleTaskMemory prototype (linked to static allocation support) */
void vApplicationGetIdleTaskMemory( StaticTask_t **ppxIdleTaskTCBBuffer, StackType_t **ppxIdleTaskStackBuffer, uint32_t *pulIdleTaskStackSize );

/* USER CODE BEGIN GET_IDLE_TASK_MEMORY */
static StaticTask_t xIdleTaskTCBBuffer;
static StackType_t xIdleStack[configMINIMAL_STACK_SIZE];

void vApplicationGetIdleTaskMemory( StaticTask_t **ppxIdleTaskTCBBuffer, StackType_t **ppxIdleTaskStackBuffer, uint32_t *pulIdleTaskStackSize )
{
  *ppxIdleTaskTCBBuffer = &xIdleTaskTCBBuffer;
  *ppxIdleTaskStackBuffer = &xIdleStack[0];
  *pulIdleTaskStackSize = configMINIMAL_STACK_SIZE;
  /* place for user code */
}
/* USER CODE END GET_IDLE_TASK_MEMORY */

/**
  * @brief  FreeRTOS initialization
  * @param  None
  * @retval None
  */
void MX_FREERTOS_Init(void) {
  /* USER CODE BEGIN Init */

  /* USER CODE END Init */
  /* Create the mutex(es) */
  /* definition and creation of I2CMutex */
  osMutexDef(I2CMutex);
  I2CMutexHandle = osMutexCreate(osMutex(I2CMutex));

  /* USER CODE BEGIN RTOS_MUTEX */
  /* add mutexes, ... */
  /* USER CODE END RTOS_MUTEX */

  /* USER CODE BEGIN RTOS_SEMAPHORES */
  /* add semaphores, ... */
  /* USER CODE END RTOS_SEMAPHORES */

  /* USER CODE BEGIN RTOS_TIMERS */
  /* start timers, add new ones, ... */
  /* USER CODE END RTOS_TIMERS */

  /* Create the queue(s) */
  /* definition and creation of inputQueue */
  osMessageQDef(inputQueue, 4, uint8_t);
  inputQueueHandle = osMessageCreate(osMessageQ(inputQueue), NULL);

  /* USER CODE BEGIN RTOS_QUEUES */
  /* add queues, ... */
  /* USER CODE END RTOS_QUEUES */

  /* Create the thread(s) */
  /* definition and creation of keypadTask */
  osThreadDef(keypadTask, StartKeypadTask, osPriorityAboveNormal, 0, 256);
  keypadTaskHandle = osThreadCreate(osThread(keypadTask), NULL);

  /* definition and creation of gameTask */
  osThreadDef(gameTask, StartGameTask, osPriorityIdle, 0, 512);
  gameTaskHandle = osThreadCreate(osThread(gameTask), NULL);

  /* USER CODE BEGIN RTOS_THREADS */
  /* add threads, ... */
  /* USER CODE END RTOS_THREADS */

}

/* USER CODE BEGIN Header_StartKeypadTask */
/**
  * @brief  Function implementing the keypadTask thread.
  * @param  argument: Not used
  * @retval None
  */
/* USER CODE END Header_StartKeypadTask */
void StartKeypadTask(void const * argument)
{
  /* USER CODE BEGIN StartKeypadTask */
	osDelay(500);

		Direction_t current_dir = DIR_NONE;
		Direction_t last_dir = DIR_NONE;
		uint8_t row_val = 0;

	  /* Infinite loop */
	  for(;;)
	  {
		  current_dir = DIR_NONE;
		  if (osMutexWait(I2CMutexHandle, osWaitForever) == osOK) {
			  if (Check_Row(ROW3) == 0x02) {
				  current_dir = DIR_UP;
				  UART_Transmit((uint8_t*)"Key pressed UP\r\n");
			  } else if (Check_Row(ROW1) == 0x02) {
				  current_dir = DIR_DOWN;
				  UART_Transmit((uint8_t*)"Key pressed DOWN\r\n");
			  } else {
				row_val = Check_Row(ROW2);
				if (row_val == 0x04) {
					current_dir = DIR_LEFT;
					UART_Transmit((uint8_t*)"Key pressed LEFT\r\n");
				} else if (row_val == 0x01) {
					current_dir = DIR_RIGHT;
					UART_Transmit((uint8_t*)"Key pressed RIGHT\r\n");
				}
			  }
			  osMutexRelease(I2CMutexHandle);
		  }
		  if (current_dir != DIR_NONE) {
			  if (current_dir != last_dir) {
				  osMessagePut(inputQueueHandle, (uint32_t) current_dir, 0);

				  UART_Transmit((uint8_t*)"Key sent\r\n");

				  last_dir = current_dir;

				  osDelay(50);
			  } else {
				  osDelay(50);
			  }
		  } else {
			  last_dir = DIR_NONE;
			  osDelay(50);
		  }
	  }
	  /* USER CODE END StartKeypadTask */
}

/* USER CODE BEGIN Header_StartGameTask */
/**
* @brief Function implementing the gameTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_StartGameTask */
void StartGameTask(void const * argument)
{
  /* USER CODE BEGIN StartGameTask */
	osDelay(100);
		srand(HAL_GetTick());

		osMutexWait(I2CMutexHandle, osWaitForever);
		oled_Init();
		oled_Fill(Black);
		oled_UpdateScreen();
		osMutexRelease(I2CMutexHandle);

		InitGame();
	  /* Infinite loop */
	  for(;;)
	  {
		  if (game_over) {
			 osMutexWait(I2CMutexHandle, osWaitForever);
			 oled_Fill(Black);
	         oled_SetCursor(30, 20);
	         oled_WriteString("GAME OVER", Font_7x10, White);
	         oled_UpdateScreen();
	         osMutexRelease(I2CMutexHandle);

	         osDelay(2000);
	         xQueueReset(inputQueueHandle);
	         InitGame();
	         continue;
		  }
	    osEvent event = osMessageGet(inputQueueHandle, 0);

	    if (event.status == osEventMessage) {
	    	ChangeDirection(event.value.v);
	    }

	    GrowSnake();
	    MoveSnake();
	    CheckCollisions();

	    if (!game_over) {
	    	osMutexWait(I2CMutexHandle, osWaitForever);

	    	oled_Fill(Black);

	    	oled_DrawSquare(0, 127, 0, BLOCK_SIZE-1, White);
	    	oled_DrawSquare(0, 127, 63-(BLOCK_SIZE-1), 63, White);
	    	oled_DrawSquare(0, BLOCK_SIZE-1, 0, 63, White);
	    	oled_DrawSquare(127-(BLOCK_SIZE-1), 127, 0, 63, White);

	        char score_buf[16];
	        sprintf(score_buf, "S: %d", score);
	        oled_SetCursor(5, 5);
	        oled_WriteString(score_buf, Font_7x10, White);

	    	uint8_t fx = food.x * BLOCK_SIZE;
	    	uint8_t fy = food.y * BLOCK_SIZE;
	    	oled_DrawSquare(fx+1, fx+BLOCK_SIZE-1, fy+1, fy+BLOCK_SIZE-1, White);

	    	for (int i = 0; i < snake.length; i++) {
	    		uint8_t sx = snake.body[i].x * BLOCK_SIZE;
	    		uint8_t sy = snake.body[i].y * BLOCK_SIZE;
	    		oled_DrawSquare(sx+1, sx+BLOCK_SIZE-1, sy+1, sy+BLOCK_SIZE-1, White);
	    	}

	    	oled_UpdateScreen();

	    	osMutexRelease(I2CMutexHandle);
	    }
	    osDelay(100);
	  }

  /* USER CODE END StartGameTask */
}

/* Private application code --------------------------------------------------*/
/* USER CODE BEGIN Application */

/* USER CODE END Application */
