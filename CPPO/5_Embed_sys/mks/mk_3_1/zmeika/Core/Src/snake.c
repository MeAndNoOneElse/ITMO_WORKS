#include "snake.h"
#include <string.h>

static uint32_t random_next(Snake *s)
{
    uint32_t x = s->random;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    return s->random = x;
}
static int occupied(const Snake *s, SnakeCell cell, unsigned count)
{
    for (unsigned i = 0; i < count; ++i)
        if (s->body[i].x == cell.x && s->body[i].y == cell.y) return 1;
    return 0;
}
static void food_place(Snake *s)
{
    if (s->length == SNAKE_CAPACITY) { s->status = GAME_WON; return; }
    /* Select an empty cell in bounded time, even when the board is almost full. */
    unsigned free_index = random_next(s) % (SNAKE_CAPACITY - s->length);
    for (uint8_t y = 0; y < SNAKE_HEIGHT; ++y)
        for (uint8_t x = 0; x < SNAKE_WIDTH; ++x) {
            SnakeCell cell = {x, y};
            if (!occupied(s, cell, s->length)) {
                if (free_index == 0) { s->food = cell; return; }
                --free_index;
            }
        }
}
void Snake_Init(Snake *s, uint32_t seed, uint16_t best)
{
    memset(s, 0, sizeof(*s));
    s->random = seed ? seed : 0x42712345u;
    s->best = best; s->length = 4;
    s->direction = s->pending = DIR_RIGHT;
    s->status = GAME_READY;
    for (unsigned i = 0; i < s->length; ++i)
        s->body[i] = (SnakeCell){(uint8_t)(SNAKE_WIDTH / 2 - i), SNAKE_HEIGHT / 2};
    food_place(s);
}
void Snake_Turn(Snake *s, SnakeDirection direction)
{
    /* At most one turn per movement tick prevents a fast 180-degree reversal. */
    if (s->status != GAME_RUNNING || s->turn_pending || direction > DIR_LEFT) return;
    if (direction == s->direction || ((direction + 2) % 4) == s->direction) return;
    s->pending = direction; s->turn_pending = 1;
}
void Snake_TogglePause(Snake *s)
{
    if (s->status == GAME_READY || s->status == GAME_PAUSED) s->status = GAME_RUNNING;
    else if (s->status == GAME_RUNNING) s->status = GAME_PAUSED;
}
void Snake_Step(Snake *s)
{
    static const int8_t dx[] = {0, 1, 0, -1}, dy[] = {-1, 0, 1, 0};
    if (s->status != GAME_RUNNING) return;
    s->direction = s->pending; s->turn_pending = 0;
    int x = s->body[0].x + dx[s->direction], y = s->body[0].y + dy[s->direction];
    if (x < 0 || x >= SNAKE_WIDTH || y < 0 || y >= SNAKE_HEIGHT) {
        s->status = GAME_OVER; return;
    }
    SnakeCell next = {(uint8_t)x, (uint8_t)y};
    int grows = next.x == s->food.x && next.y == s->food.y;
    /* The old tail is free on this tick unless food makes the snake grow. */
    if (occupied(s, next, s->length - (grows ? 0 : 1))) {
        s->status = GAME_OVER; return;
    }
    if (grows) ++s->length;
    memmove(&s->body[1], &s->body[0], (s->length - 1) * sizeof(SnakeCell));
    s->body[0] = next;
    if (grows) {
        ++s->score;
        if (s->score > s->best) s->best = s->score;
        food_place(s);
    }
}
uint32_t Snake_Period(const Snake *s)
{
    uint32_t reduction = (s->score / 3u) * 20u;
    return reduction >= 220u ? 80u : 300u - reduction;
}
