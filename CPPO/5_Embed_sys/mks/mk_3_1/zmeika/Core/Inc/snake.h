#ifndef SNAKE_H
#define SNAKE_H
#include <stdint.h>
#define SNAKE_WIDTH 30
#define SNAKE_HEIGHT 12
#define SNAKE_CAPACITY (SNAKE_WIDTH * SNAKE_HEIGHT)
typedef struct { uint8_t x, y; } SnakeCell;
typedef enum { DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT } SnakeDirection;
typedef enum { GAME_READY, GAME_RUNNING, GAME_PAUSED, GAME_OVER, GAME_WON } SnakeStatus;
typedef struct {
    SnakeCell body[SNAKE_CAPACITY], food;
    uint16_t length, score, best;
    SnakeDirection direction, pending;
    SnakeStatus status;
    uint8_t turn_pending;
    uint32_t random;
} Snake;
void Snake_Init(Snake *s, uint32_t seed, uint16_t best);
void Snake_Turn(Snake *s, SnakeDirection direction);
void Snake_TogglePause(Snake *s);
void Snake_Step(Snake *s);
uint32_t Snake_Period(const Snake *s);
#endif
