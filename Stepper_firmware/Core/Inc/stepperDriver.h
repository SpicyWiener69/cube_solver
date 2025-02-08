#include <stdint.h>
#include "stm32f4xx.h"

#define ARRAY_SIZE 1000

typedef struct
{
    uint16_t data[ARRAY_SIZE];
    size_t size;
} ArrayStruct;

typedef struct
{
    uint16_t steps;
    uint16_t accel;
    uint16_t lowSpeedInterval;
    uint16_t highSpeedInterval;
    
} Profile_param;



typedef struct{
    uint32_t index; 
    uint8_t pinstate;
    uint32_t start_time;
} runState;

typedef struct{


}Motor_param;


void setPin(GPIO_TypeDef *GPIOx, uint32_t pin);
void resetPin(GPIO_TypeDef *GPIOx, uint32_t pin);


uint32_t ResetUsTimer(void);
uint32_t GetUsTime(void);
void generateTrapezoidProfile(Profile_param* param, ArrayStruct* profile);