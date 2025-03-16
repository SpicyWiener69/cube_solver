#ifndef SERVO_H
#define SERVO_H

#include "stm32f4xx.h"
#include "gpio_def.h"

typedef struct
{   uint8_t id;
    //uint16_t pwm_pin;
    GPIO_TypeDef *gpio;
    int16_t deg;
    int16_t home_deg;
} servo_config_T;

servo_config_T servo_Init(void);
/*timers*/

//void set_servo_home() {}

//moveServoMotorRelative(int16_t deg);

servo_config_T moveServoMotorAbs(servo_config_T servo, int16_t deg);

#endif