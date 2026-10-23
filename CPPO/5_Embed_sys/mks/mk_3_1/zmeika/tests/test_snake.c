#include "snake.h"
#include "game_view.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static void invariant(const Snake *s)
{
    assert(s->length >= 4 && s->length <= SNAKE_CAPACITY);
    for (unsigned i = 0; i < s->length; ++i) {
        assert(s->body[i].x < SNAKE_WIDTH && s->body[i].y < SNAKE_HEIGHT);
        for (unsigned j = i + 1; j < s->length; ++j)
            assert(s->body[i].x != s->body[j].x || s->body[i].y != s->body[j].y);
        if (s->status != GAME_WON)
            assert(s->food.x != s->body[i].x || s->food.y != s->body[i].y);
    }
    assert(Snake_Period(s) >= 80 && Snake_Period(s) <= 300);
}
static void preview(const Snake *s, const char *name)
{
    struct { unsigned char prefix[16], pixels[1024], suffix[16]; } guarded;
    memset(&guarded, 0xA5, sizeof(guarded));
    Game_Render(s, guarded.pixels);
    for (unsigned i = 0; i < 16; ++i) assert(guarded.prefix[i] == 0xA5 && guarded.suffix[i] == 0xA5);
    FILE *f = fopen(name, "wb");
    assert(f);
    fprintf(f, "P1\n128 64\n");
    for (unsigned y = 0; y < 64; ++y) {
        for (unsigned x = 0; x < 128; ++x)
            fprintf(f, "%d ", !(guarded.pixels[x + (y / 8) * 128] & (1u << (y % 8))));
        fputc('\n', f);
    }
    fclose(f);
}
int main(void)
{
    Snake s, old;
    Snake_Init(&s, 0, 12); invariant(&s);
    assert(s.best == 12 && s.status == GAME_READY);
    old = s; Snake_Step(&s); assert(memcmp(&old, &s, sizeof(s)) == 0);
    preview(&s, "tests/ready.pbm");
    Snake_TogglePause(&s); assert(s.status == GAME_RUNNING);
    Snake_Turn(&s, DIR_LEFT); assert(s.pending == DIR_RIGHT);
    Snake_Turn(&s, DIR_UP); Snake_Turn(&s, DIR_LEFT);
    assert(s.pending == DIR_UP);
    Snake_Step(&s); assert(s.body[0].y == SNAKE_HEIGHT / 2 - 1);
    Snake_TogglePause(&s); old = s; Snake_Step(&s);
    assert(memcmp(&old, &s, sizeof(s)) == 0);
    preview(&s, "tests/paused.pbm");
    Snake_TogglePause(&s); assert(s.status == GAME_RUNNING);
    s.food = (SnakeCell){s.body[0].x, (uint8_t)(s.body[0].y - 1)};
    Snake_Step(&s); assert(s.length == 5 && s.score == 1 && s.best == 12); invariant(&s);
    preview(&s, "tests/running.pbm");
    s.body[0].y = 0; Snake_Step(&s); assert(s.status == GAME_OVER);
    preview(&s, "tests/over.pbm");

    /* The tail cell is legal only when the tail leaves during the same tick. */
    Snake_Init(&s, 42, 0); s.status = GAME_RUNNING;
    s.body[0] = (SnakeCell){1,1}; s.body[1] = (SnakeCell){1,2};
    s.body[2] = (SnakeCell){0,2}; s.body[3] = (SnakeCell){0,1};
    s.direction = s.pending = DIR_LEFT; s.food = (SnakeCell){5,5};
    Snake_Step(&s); assert(s.status == GAME_RUNNING && s.body[0].x == 0); invariant(&s);
    /* A non-tail body cell still causes a collision. */
    s.length = 5; s.body[4] = (SnakeCell){2,2};
    s.direction = s.pending = DIR_DOWN;
    Snake_Step(&s); assert(s.status == GAME_OVER);

    /* Last free cell: grow to capacity without rejection-sampling lockup. */
    Snake_Init(&s, 99, 0); s.status = GAME_RUNNING; s.length = SNAKE_CAPACITY - 1;
    unsigned n = 0;
    for (unsigned y = 0; y < SNAKE_HEIGHT; ++y)
        for (unsigned x = 0; x < SNAKE_WIDTH; ++x)
            if (x || y) s.body[n++] = (SnakeCell){x,y};
    s.food = (SnakeCell){0,0}; s.direction = s.pending = DIR_LEFT;
    Snake_Step(&s); assert(s.length == SNAKE_CAPACITY && s.status == GAME_WON); invariant(&s);
    preview(&s, "tests/won.pbm");
    s.score = 300; assert(Snake_Period(&s) == 80);

    for (unsigned seed = 1; seed <= 100; ++seed) {
        Snake_Init(&s, seed, 0); Snake_TogglePause(&s);
        unsigned rng = seed;
        for (unsigned tick = 0; tick < 500; ++tick) {
            rng = rng * 1664525u + 1013904223u;
            Snake_Turn(&s, (SnakeDirection)((rng >> 24) % 4));
            Snake_Step(&s); invariant(&s);
            if (s.status == GAME_OVER) { Snake_Init(&s, rng, s.best); Snake_TogglePause(&s); }
        }
    }
    puts("PASS: initialization, pause, turns, growth, wall, tail, body, victory, speed, 50000 invariant checks, render bounds");
    return 0;
}
