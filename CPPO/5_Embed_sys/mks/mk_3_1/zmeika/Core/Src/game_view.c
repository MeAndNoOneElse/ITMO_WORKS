#include "game_view.h"
#include <string.h>
#include <stdio.h>
/* Original compact 3x5 glyphs, rows packed from most significant to least. */
static const char alphabet[] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ:- ";
static const uint16_t glyphs[] = {
  0x7B6F,0x2492,0x73E7,0x73CF,0x5BC9,0x79CF,0x79EF,0x7249,0x7BEF,0x7BCF,
  0x2BED,0x6BAE,0x7927,0x6B6E,0x79A7,0x79A4,0x796F,0x5BED,0x7497,0x124F,
  0x5BAD,0x4927,0x5FED,0x5FFD,0x7B6F,0x7BE4,0x7B7B,0x7BAD,0x79CF,0x7492,
  0x5B6F,0x5B6A,0x5BFD,0x5AAD,0x5A92,0x72A7,0x0410,0x01C0,0x0000
};
static void pixel(uint8_t *fb, int x, int y, int on)
{
    if (x < 0 || x >= 128 || y < 0 || y >= 64) return;
    uint8_t mask = (uint8_t)(1u << (y & 7));
    if (on) fb[x + (y / 8) * 128] |= mask;
    else fb[x + (y / 8) * 128] &= (uint8_t)~mask;
}
static void rect(uint8_t *fb, int x, int y, int w, int h, int on)
{
    for (int j = y; j < y + h; ++j)
        for (int i = x; i < x + w; ++i) pixel(fb, i, j, on);
}
static void text(uint8_t *fb, int x, int y, const char *s)
{
    for (; *s; ++s, x += 4) {
        const char *g = strchr(alphabet, *s);
        uint16_t bits = g ? glyphs[g - alphabet] : 0;
        for (int row = 0; row < 5; ++row)
            for (int col = 0; col < 3; ++col)
                pixel(fb, x + col, y + row, (bits >> (14 - row * 3 - col)) & 1);
    }
}
void Game_Render(const Snake *s, uint8_t fb[1024])
{
    char line[32];
    memset(fb, 0, 1024);
    snprintf(line, sizeof(line), "SCORE:%u BEST:%u", (unsigned)s->score, (unsigned)s->best);
    text(fb, 2, 1, line);
    rect(fb, 2, 9, 122, 1, 1); rect(fb, 2, 58, 122, 1, 1);
    rect(fb, 2, 9, 1, 50, 1); rect(fb, 123, 9, 1, 50, 1);
    for (unsigned i = 0; i < s->length; ++i) {
        int x = 3 + 4 * s->body[i].x, y = 10 + 4 * s->body[i].y;
        rect(fb, x, y, 3, 3, 1);
        if (i == 0) pixel(fb, x + 1, y + 1, 0);
    }
    if (s->status != GAME_WON) {
        int x = 3 + 4 * s->food.x, y = 10 + 4 * s->food.y;
        rect(fb, x + 1, y, 1, 3, 1); rect(fb, x, y + 1, 3, 1, 1);
    }
    if (s->status != GAME_RUNNING) {
        const char *title = s->status == GAME_READY ? "SNAKE" : s->status == GAME_PAUSED ? "PAUSED" :
                            s->status == GAME_WON ? "YOU WIN" : "GAME OVER";
        const char *help = s->status == GAME_READY || s->status == GAME_PAUSED ? "SB6: PLAY" : "SB6: RETRY";
        rect(fb, 33, 23, 62, 22, 0);
        text(fb, 64 - (int)strlen(title) * 2, 26, title);
        text(fb, 64 - (int)strlen(help) * 2, 36, help);
    }
}
