#ifndef BOARD_GAME_H
#define BOARD_GAME_H
#include "main.h"
#include "snake.h"
/* Return values: 1..12 = SB1..SB12, 0 = released, -1 = bus error/multiple keys. */
void Board_Init(void);
int Board_ReadKey(void);
int Board_DisplayInit(void);
int Board_DisplayPage(unsigned page, const uint8_t *pixels);
void Board_Leds(SnakeStatus status, int fault);
extern volatile uint32_t board_i2c_errors;
typedef enum { SOUND_OFF, SOUND_APPLE, SOUND_GAME_OVER } BoardSound;
void Board_SoundPlay(BoardSound sound);
void Board_SoundUpdate(void);
#endif
