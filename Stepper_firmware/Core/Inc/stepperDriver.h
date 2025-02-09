#include <stdint.h>
#include "stm32f4xx.h"

#define ARRAY_SIZE 4000

typedef struct
{
    uint16_t data[ARRAY_SIZE];
    uint8_t direction;
    size_t size;
} ArrayStruct;

// typedef struct
// {
//     uint16_t steps;
//     uint16_t accel;
//     uint16_t lowSpeedInterval;
//     uint16_t highSpeedInterval;
    
// } Profile_param;



// typedef struct{
//     uint32_t index; 
//     uint8_t pinstate;
//     uint32_t start_time;
// } runState;

typedef struct{
    GPIO_TypeDef* GPIO;
    uint8_t dirPin;
    uint8_t stepPin;
    ArrayStruct* accelProfilePtr;
    uint16_t steps;
    uint16_t accel;
    uint16_t lowSpeedInterval;
    uint16_t highSpeedInterval;
    uint32_t _index; 
    uint8_t _pinstate;
    volatile uint32_t _start_time;
}StepperMotor;



// static void setPin(GPIO_TypeDef *GPIOx, uint32_t pin);
// static void resetPin(GPIO_TypeDef *GPIOx, uint32_t pin);

uint32_t ResetUsTimer(void);
uint32_t GetUsTime(void);

uint8_t moveMotor(StepperMotor* motor);
void generateTrapezoidProfile(StepperMotor motor, ArrayStruct* profile); 