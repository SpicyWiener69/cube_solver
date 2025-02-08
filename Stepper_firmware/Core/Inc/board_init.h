//#include "stm32f4xx_hal.h"
#include "stm32f4xx.h"
#include "gpio_def.h"

#define BUTTONPIN 8

void SystemClock_Config(void);
void EXTI_Init(void);
void NVIC_Init(void);
void GPIO_Init(void);
void MhzTimer_Init(void);  