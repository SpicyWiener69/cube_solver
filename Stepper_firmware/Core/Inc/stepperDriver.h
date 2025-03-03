#include <stdint.h>
#include "stm32f4xx.h"

#define ARRAY_SIZE 400
#define MAX_TASK 10
#define MAX_STEPPER 6

typedef struct
{
    uint16_t data[ARRAY_SIZE];
    // uint8_t direction;
    size_t size;
} ArrayStruct_T;

typedef struct
{
    uint8_t id;
    GPIO_TypeDef *GPIO;
    uint8_t dirPin;
    uint8_t stepPin;

} Motor_config_T;

typedef struct
{
    uint8_t id;
    uint16_t steps;
    uint8_t direction;
    uint16_t accel;
    ArrayStruct_T* profileP;
    uint16_t lowSpeedInterval;
    uint16_t highSpeedInterval;
    uint32_t _index;
    volatile uint8_t _pinstate;
    volatile uint32_t _start_time;
    uint16_t stepsPer360;
} Task_T;

typedef struct
{
    Task_T task[MAX_TASK];
    uint8_t length;
} Task_lst_T;

typedef struct
{
    Motor_config_T Motor_config[MAX_STEPPER];
    uint8_t length;
} Motor_lst_T;

// typedef struct
// {
//     uint8_t id;
//     uint16_t steps;
//     uint8_t direction;
// } Task_T;

// static void setPin(GPIO_TypeDef *GPIOx, uint32_t pin);
// static void resetPin(GPIO_TypeDef *GPIOx, uint32_t pin);

uint32_t ResetUsTimer(void);
uint32_t GetUsTime(void);
ArrayStruct_T generateTrapezoidProfile(Task_T task);
void updateTaskProfilePtr(Task_T* task,ArrayStruct_T* profile);
uint8_t moveMotor(Motor_config_T motor,Task_T task);