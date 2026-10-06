#include "main.h"
#include "tm1637.h"
#include "keyboard.h"

volatile uint32_t tickCount;
uint32_t last_display_update;
uint16_t counter;
char lastKey;
uint32_t lastScanTime;

// --- calculator state ---
char calc_op = '+';
uint8_t calc_first = 0;
uint8_t calc_second = 0;
uint8_t calc_stage = 0;
int16_t calc_result = 0;
uint8_t calc_show_result = 0;
uint8_t calc_first_full = 0;
uint8_t calc_second_full = 0;

void osSystickHandler(void) {
  tickCount++;
}

void initGPIO(void) {
  RCC->AHBENR |= RCC_AHBENR_GPIOAEN | RCC_AHBENR_GPIOBEN;

  GPIOA->MODER = (GPIOA->MODER & ~(3 << 10)) | (1 << 10);
  GPIOA->OTYPER &= ~(1 << 5);
  GPIOA->OSPEEDR |= (1 << 10);
}

void initUSART2(void) {
  RCC->APB1ENR |= RCC_APB1ENR_USART2EN;

  GPIOA->MODER = (GPIOA->MODER & ~(0xF << 4)) | (0xA << 4);
  GPIOA->AFR[0] = (GPIOA->AFR[0] & ~(0xFF << 8)) | (1 << 8) | (1 << 12);

  USART2->BRR = 417;
  USART2->CR1 = USART_CR1_TE | USART_CR1_UE;
}

void initSysTick(void) {
  SysTick->LOAD = 47999;
  SysTick->VAL = 0;
  SysTick->CTRL = (1 << 2) | (1 << 1) | (1 << 0);
}

int _write(int file, uint8_t *ptr, int len) {
  (void)file;
  for (int i = 0; i < len; i++) {
    while (!(USART2->ISR & USART_ISR_TXE));
    USART2->TDR = ptr[i];
  }
  return len;
}

void checkTickCount(void) {
  static uint32_t last = 0;
  if (tickCount - last >= 2000) {
    last = tickCount;
    GPIOA->ODR ^= (1 << 5);
    printf("tickCount = %lu\n", (unsigned long)tickCount);
  }
}

int main(void) {
  initGPIO();
  initUSART2();
  initSysTick();
  initKeyboard();
  tm1637_init();

  printf("Calculator ready\n");

  while (1) {
        scanKeyboard();
  }

  return 0;
}