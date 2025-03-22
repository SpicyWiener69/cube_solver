#ifndef SERVO_H
#define SERVO_H

#include "stm32f4xx.h"
#include "gpio_def.h"

#define CLAW_CLOSE_ENDPOINT 130
#define CLAW_OPEN_ENDPOINT 0




typedef struct
{   uint8_t id;
    //uint16_t pwm_pin;
    GPIO_TypeDef *gpio;
    int16_t abs_deg;
    int16_t home_deg;
} servo_config_T;

servo_config_T servo_Init(int16_t deg);
/*timers*/

//void set_servo_home() {}

//moveServoMotorRelative(int16_t deg);

servo_config_T moveServoMotorAbs(servo_config_T servo, int16_t deg);
servo_config_T moveServoMotorRelative(servo_config_T servo, int16_t relative_deg);

#endif