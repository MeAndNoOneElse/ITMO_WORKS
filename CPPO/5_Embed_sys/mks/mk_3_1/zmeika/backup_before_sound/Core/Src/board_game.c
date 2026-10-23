#include "board_game.h"
extern I2C_HandleTypeDef hi2c1;
#define PCA_DISPLAY 0xE0u
#define PCA_KEYS 0xE2u
#define OLED 0x78u
volatile uint32_t board_i2c_errors;

static int write_reg(uint16_t address, uint8_t reg, uint8_t value)
{
    if (HAL_I2C_Mem_Write(&hi2c1, address, reg, I2C_MEMADD_SIZE_8BIT, &value, 1, 10) == HAL_OK) return 1;
    ++board_i2c_errors; return 0;
}
static int read_reg(uint16_t address, uint8_t reg, uint8_t *value)
{
    if (HAL_I2C_Mem_Read(&hi2c1, address, reg, I2C_MEMADD_SIZE_8BIT, value, 1, 10) == HAL_OK) return 1;
    ++board_i2c_errors; return 0;
}
void Board_Init(void)
{
    /* A debug reset resets the MCU, not the external I2C slaves. A slave may
       still be holding SDA after an interrupted read. Clock it to a STOP
       before enabling the STM32 I2C state machine. */
    HAL_I2C_DeInit(&hi2c1);
    __HAL_RCC_GPIOB_CLK_ENABLE();
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8 | GPIO_PIN_9, GPIO_PIN_SET);
    GPIO_InitTypeDef gpio = {0};
    gpio.Pin = GPIO_PIN_8 | GPIO_PIN_9;
    gpio.Mode = GPIO_MODE_OUTPUT_OD;
    gpio.Pull = GPIO_PULLUP;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOB, &gpio);
    HAL_Delay(1);
    for (unsigned pulse = 0; pulse < 9; ++pulse) {
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_RESET);
        HAL_Delay(1);
        HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);
        HAL_Delay(1);
    }
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_9, GPIO_PIN_RESET);
    HAL_Delay(1);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);
    HAL_Delay(1);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_9, GPIO_PIN_SET);
    HAL_Delay(1);
    __HAL_RCC_I2C1_FORCE_RESET();
    __HAL_RCC_I2C1_RELEASE_RESET();
    if (HAL_I2C_Init(&hi2c1) != HAL_OK) Error_Handler();
    /* The PCA9538 reset net is pulled high on the board; leave it released. */
    if (!write_reg(PCA_KEYS, 3, 0xFF) || !write_reg(PCA_KEYS, 2, 0) ||
        !write_reg(PCA_KEYS, 1, 0)) Error_Handler();
}
int Board_ReadKey(void)
{
    int key = 0;
    for (unsigned row = 0; row < 4; ++row) {
        uint8_t inputs;
        /* Only the selected row drives low; all other lines are high impedance. */
        if (!write_reg(PCA_KEYS, 3, (uint8_t)~(1u << row)) ||
            !read_reg(PCA_KEYS, 0, &inputs)) {
            (void)write_reg(PCA_KEYS, 3, 0xFF); return -1;
        }
        for (unsigned col = 0; col < 3; ++col) {
            if (!(inputs & (1u << (4 + col)))) {
                if (key != 0) key = -1;
                else key = (int)(col * 4 + row + 1);
            }
        }
    }
    if (!write_reg(PCA_KEYS, 3, 0xFF)) return -1;
    return key;
}
int Board_DisplayInit(void)
{
    uint8_t output, config;
    if (!read_reg(PCA_DISPLAY, 1, &output) || !read_reg(PCA_DISPLAY, 3, &config)) return 0;
    /* Modify only P0: P1 and DIP-switch/IMU lines remain untouched. */
    if (!write_reg(PCA_DISPLAY, 1, output | 1u) ||
        !write_reg(PCA_DISPLAY, 3, config & 0xFEu)) return 0;
    HAL_Delay(1);
    if (!write_reg(PCA_DISPLAY, 1, output & 0xFEu)) return 0;
    HAL_Delay(1);
    if (!write_reg(PCA_DISPLAY, 1, output | 1u)) return 0;
    HAL_Delay(2);
    uint8_t commands[] = {0xAE,0x20,0x02,0xB0,0xC8,0x00,0x10,0x40,
        0x81,0x7F,0xA1,0xA6,0xA8,0x3F,0xA4,0xD3,0x00,
        0xD5,0x80,0xD9,0x22,0xDA,0x12,0xDB,0x20,0x8D,0x14,0xAF};
    if (HAL_I2C_Mem_Write(&hi2c1, OLED, 0, 1, commands, sizeof(commands), 20) == HAL_OK) return 1;
    ++board_i2c_errors; return 0;
}
int Board_DisplayPage(unsigned page, const uint8_t *pixels)
{
    uint8_t command[] = {(uint8_t)(0xB0u + page), 0, 0x10};
    if (page >= 8) return 0;
    if (HAL_I2C_Mem_Write(&hi2c1, OLED, 0, 1, command, sizeof(command), 10) == HAL_OK &&
        HAL_I2C_Mem_Write(&hi2c1, OLED, 0x40, 1, (uint8_t *)pixels, 128, 25) == HAL_OK) return 1;
    ++board_i2c_errors; return 0;
}
void Board_Leds(SnakeStatus status, int fault)
{
    HAL_GPIO_WritePin(GPIOD, GPIO_PIN_13, status == GAME_RUNNING ? GPIO_PIN_SET : GPIO_PIN_RESET);
    /* PD14/PD15 drive opposite ends of the bicolour LED. */
    HAL_GPIO_WritePin(GPIOD, GPIO_PIN_14, fault || status == GAME_OVER ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOD, GPIO_PIN_15, !fault && status != GAME_OVER && status != GAME_RUNNING ? GPIO_PIN_SET : GPIO_PIN_RESET);
}
