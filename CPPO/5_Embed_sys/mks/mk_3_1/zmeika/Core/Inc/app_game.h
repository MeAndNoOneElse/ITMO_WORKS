#ifndef APP_GAME_H
#define APP_GAME_H
void App_Init(void);
void App_InputTask(void const *argument);
void App_GameTask(void const *argument);
void App_DisplayTask(void const *argument);
#endif
