#include "keyboard.h"
#include "tm1637.h"

void initKeyboard(void) {
  // R1..R4 -> выходы с открытым стоком: PB7, PB6, PA10, PB3
  GPIOB->MODER = (GPIOB->MODER & ~(3U << (7 * 2))) | (1U << (7 * 2));
  GPIOB->MODER = (GPIOB->MODER & ~(3U << (6 * 2))) | (1U << (6 * 2));
  GPIOA->MODER = (GPIOA->MODER & ~(3U << (10 * 2))) | (1U << (10 * 2));
  GPIOB->MODER = (GPIOB->MODER & ~(3U << (3 * 2))) | (1U << (3 * 2));

  GPIOB->OTYPER |= (1 << 7) | (1 << 6) | (1 << 3);
  GPIOA->OTYPER |= (1 << 10);

  // C1..C3 -> входы с подтяжкой: PB10, PB4, PB5
  GPIOB->MODER &= ~(3U << (10 * 2) | 3U << (4 * 2) | 3U << (5 * 2));
  GPIOB->PUPDR = (GPIOB->PUPDR & ~(3U << (10 * 2))) | (1U << (10 * 2));
  GPIOB->PUPDR = (GPIOB->PUPDR & ~(3U << (4 * 2)))  | (1U << (4 * 2));
  GPIOB->PUPDR = (GPIOB->PUPDR & ~(3U << (5 * 2)))  | (1U << (5 * 2));

  lastKey = '\0';
  lastScanTime = 0;
}

char readKey(void) {
  const uint8_t rows[] = {7, 6, 10, 3};   // PB7, PB6, PA10, PB3
  const uint8_t cols[] = {10, 4, 5};      // PB10, PB4, PB5
  const char keymap[4][3] = {
    {'1', '2', '3'},
    {'4', '5', '6'},
    {'7', '8', '9'},
    {'*', '0', '#'}
  };

  for (uint8_t i = 0; i < 4; i++) {
    // активируем строку (низкий уровень)
    if (rows[i] != 10) {
      GPIOB->BSRR = (1 << (rows[i] + 16));
    } else {
      GPIOA->BSRR = (1 << (rows[i] + 16));
    }

    for (volatile int d = 0; d < 200; d++);

    for (uint8_t j = 0; j < 3; j++) {
      if ((GPIOB->IDR & (1 << cols[j])) == 0) {
        // деактивируем строку
        if (rows[i] != 10) {
          GPIOB->BSRR = (1 << rows[i]);
        } else {
          GPIOA->BSRR = (1 << rows[i]);
        }
        return keymap[i][j];
      }
    }

    if (rows[i] != 10) {
      GPIOB->BSRR = (1 << rows[i]);
    } else {
      GPIOA->BSRR = (1 << rows[i]);
    }
  }

  return '\0';
}

void scanKeyboard(void) {
  if (tickCount - lastScanTime > 100) {
    lastScanTime = tickCount;
    char key = readKey();

    if (key == '\0') {
      lastKey = '\0';
      return;
    }

    if (key == lastKey) {
      return;
    }

    lastKey = key;
    printf("Pressed: %c  (stage=%d first=%d second=%d op=%c)\n",
           key, calc_stage, calc_first, calc_second, calc_op);

    // ---------- ЦИФРЫ ----------
    if (key >= '0' && key <= '9') {
      uint8_t digit = key - '0';

      switch (calc_stage) {
        case 0:  // первый операнд, первая цифра
          calc_first = digit;
          calc_stage = 1;
          tm1637_display_number(calc_first);
          break;

        case 1:  // первый операнд, вторая цифра
          if (!calc_first_full) {
            calc_first = calc_first * 10 + digit;
            calc_first_full = 1;
            tm1637_display_number(calc_first);
          }
          break;

        case 3:  // второй операнд, первая цифра
          calc_second = digit;
          calc_stage = 4;
          tm1637_display_number(calc_second);
          break;

        case 4:  // второй операнд, вторая цифра
          if (!calc_second_full) {
            calc_second = calc_second * 10 + digit;
            calc_second_full = 1;
            calc_stage = 5;
            tm1637_display_number(calc_second);
          }
          break;

        default:
          break;
      }
    }
    // ---------- ЗВЁЗДОЧКА ----------
    else if (key == '*') {
      if (calc_stage == 1) {
        // фиксируем первый операнд, начинаем выбор операции
        calc_op = '+';
        calc_stage = 3;
        printf("Operation set to: %c\n", calc_op);
      } else if (calc_stage == 3 || calc_stage == 4) {
        // циклическое переключение операции
        if (calc_op == '+')      calc_op = '-';
        else if (calc_op == '-') calc_op = '*';
        else if (calc_op == '*') calc_op = '/';
        else                     calc_op = '+';

        printf("Operation set to: %c\n", calc_op);
      }
    }
    // ---------- РЕШЁТКА ----------
    else if (key == '#') {
      if (calc_stage == 4 || calc_stage == 5) {
        switch (calc_op) {
          case '+': calc_result = calc_first + calc_second; break;
          case '-': calc_result = calc_first - calc_second; break;
          case '*': calc_result = calc_first * calc_second; break;
          case '/':
            if (calc_second == 0) calc_result = 0;
            else                  calc_result = calc_first / calc_second;
            break;
        }

        printf("Result: %d\n", calc_result);
        tm1637_display_result(calc_result);

        // сброс
        calc_stage = 0;
        calc_first = 0;
        calc_second = 0;
        calc_result = 0;
        calc_op = '+';
        calc_first_full = 0;
        calc_second_full = 0;
      } else {
        printf("# ignored: stage=%d\n", calc_stage);
      }
    }
  }
}