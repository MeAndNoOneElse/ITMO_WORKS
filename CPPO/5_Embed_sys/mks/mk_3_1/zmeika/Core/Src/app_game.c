#include "app_game.h"
#include "board_game.h"
#include "game_view.h"
#include "cmsis_os.h"
#include "queue.h"
#include "semphr.h"

static QueueHandle_t input_queue, frame_queue;
static SemaphoreHandle_t bus_mutex;
static Snake game;
static volatile uint8_t keyboard_fault, display_fault;
volatile uint32_t input_dropped;

void App_Init(void)
{
    bus_mutex = xSemaphoreCreateMutex();
    input_queue = xQueueCreate(8, sizeof(uint8_t));
    frame_queue = xQueueCreate(1, sizeof(Snake));
    if (!bus_mutex || !input_queue || !frame_queue) Error_Handler();
}
void App_InputTask(void const *argument)
{
    (void)argument;
    TickType_t wake = xTaskGetTickCount();
    int candidate = 0, stable = 0;
    unsigned count = 0;
    for (;;) {
        xSemaphoreTake(bus_mutex, portMAX_DELAY);
        int key = Board_ReadKey();
        xSemaphoreGive(bus_mutex);
        keyboard_fault = key < 0;
        if (key < 0) { count = 0; candidate = -1; }
        else {
            if (key != candidate) { candidate = key; count = 1; }
            else if (count < 3) ++count;
            if (count == 3 && stable != key) {
                stable = key;
                if (key != 0) {
                    uint8_t event = (uint8_t)key;
                    if (xQueueSend(input_queue, &event, 0) != pdPASS) ++input_dropped;
                }
            }
        }
        vTaskDelayUntil(&wake, pdMS_TO_TICKS(10));
    }
}
void App_GameTask(void const *argument)
{
    (void)argument;
    Snake_Init(&game, HAL_GetTick() ^ 0x427u, 0);
    xQueueOverwrite(frame_queue, &game);
    TickType_t last = xTaskGetTickCount();
    for (;;) {
        Board_SoundUpdate();
        TickType_t now = xTaskGetTickCount(), wait = pdMS_TO_TICKS(100);
        if (game.status == GAME_RUNNING) {
            TickType_t period = pdMS_TO_TICKS(Snake_Period(&game));
            TickType_t elapsed = now - last;
            wait = elapsed >= period ? 0 : period - elapsed;
        }
        /* Service sound deadlines without blocking the movement or input. */
        if (wait > pdMS_TO_TICKS(10)) wait = pdMS_TO_TICKS(10);
        uint8_t key;
        int changed = 0;
        if (xQueueReceive(input_queue, &key, wait) == pdPASS) {
            SnakeStatus old = game.status;
            if (key == 8 || (key == 6 && (old == GAME_OVER || old == GAME_WON))) {
                Board_SoundPlay(SOUND_OFF);
                uint16_t best = game.best;
                Snake_Init(&game, (uint32_t)xTaskGetTickCount() ^ game.random, best);
                game.status = GAME_RUNNING;
                last = xTaskGetTickCount();
                xQueueReset(input_queue);
            } else if (key == 6) {
                Board_SoundPlay(SOUND_OFF);
                Snake_TogglePause(&game);
                last = xTaskGetTickCount();
            } else if (key == 5) Snake_Turn(&game, DIR_UP);
            else if (key == 7) Snake_Turn(&game, DIR_DOWN);
            else if (key == 2) Snake_Turn(&game, DIR_LEFT);
            else if (key == 10) Snake_Turn(&game, DIR_RIGHT);
            changed = 1;
        }
        now = xTaskGetTickCount();
        if (game.status == GAME_RUNNING && now - last >= pdMS_TO_TICKS(Snake_Period(&game))) {
            uint16_t score = game.score;
            Snake_Step(&game); last = now; changed = 1;
            if (game.status == GAME_OVER) Board_SoundPlay(SOUND_GAME_OVER);
            else if (game.score > score) Board_SoundPlay(SOUND_APPLE);
        }
        if (changed) xQueueOverwrite(frame_queue, &game);
        Board_Leds(game.status, keyboard_fault || display_fault);
    }
}
void App_DisplayTask(void const *argument)
{
    (void)argument;
    static Snake frame;
    static uint8_t fb[1024];
    int initialized = 0;
    /* Game state is copied through a length-one queue, never accessed concurrently. */
    xQueueReceive(frame_queue, &frame, portMAX_DELAY);
    for (;;) {
        if (!initialized) {
            xSemaphoreTake(bus_mutex, portMAX_DELAY);
            initialized = Board_DisplayInit();
            xSemaphoreGive(bus_mutex);
        }
        Game_Render(&frame, fb);
        if (initialized) {
            for (unsigned page = 0; page < 8; ++page) {
                xSemaphoreTake(bus_mutex, portMAX_DELAY);
                int ok = Board_DisplayPage(page, fb + 128 * page);
                xSemaphoreGive(bus_mutex);
                if (!ok) { initialized = 0; break; }
            }
        }
        display_fault = !initialized;
        if (!initialized) osDelay(500);
        /* Also refresh periodically so a reconnected display can recover. */
        xQueueReceive(frame_queue, &frame, pdMS_TO_TICKS(250));
    }
}
