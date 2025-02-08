#include "stepperDriver.h"


uint32_t ResetUsTimer(void)
{
    TIM2->CNT = 0;
    return 0;
}

uint32_t GetUsTime(void)
{
    return TIM2->CNT;
}

void togglePin(GPIO_TypeDef *GPIOx, uint32_t pin)
{
    /*read data from reg*/
    uint32_t data = GPIOx->ODR;
    if (data & (1 << pin)) // pinstate = 1
    {
        GPIOx->BSRR = 1 << (16 + pin);  
    }
    else
    {
        GPIOx->BSRR = 1 << (pin);
    }
}

void setPin(GPIO_TypeDef *GPIOx, uint32_t pin)
{   
    GPIOx->BSRR = 1 << (pin);
}

void resetPin(GPIO_TypeDef *GPIOx, uint32_t pin)
{
    GPIOx->BSRR = 1 << (16 + pin);
}

// void generateTrapezoidProfile( Profile_param* param, ArrayStruct* profile) {
//     if (steps > ARRAY_SIZE || profile == NULL) return;
//     uint32_t accelSteps = 0;
//     uint32_t decelSteps = 0;
//     uint32_t flatSteps = 0;

//     // Compute the number of steps required to accelerate
//     while ((lowSpeedInterval - accelSteps * accel) > highSpeedInterval) {
//         accelSteps++;
//     }

//     decelSteps = accelSteps;
//     flatSteps = (steps > 2 * accelSteps) ? (steps - 2 * accelSteps) : 0;

//     profile->size = steps;
//     uint32_t interval = lowSpeedInterval;
//     size_t index = 0;

//     // Acceleration Phase
//     for (; index < accelSteps; index++) {
//         interval = lowSpeedInterval - (index * accel);
//         if (interval < highSpeedInterval) interval = highSpeedInterval;
//         profile->data[index] = interval;
//     }

//     // Constant Speed Phase
//     for (size_t i = 0; i < flatSteps; i++, index++) {
//         profile->data[index] = highSpeedInterval;
//     }

//     // Deceleration Phase
//     for (size_t i = 0; i < decelSteps; i++, index++) {
//         interval = highSpeedInterval + (i * accel);
//         if (interval > lowSpeedInterval) interval = lowSpeedInterval;
//         profile->data[index] = interval;
//     }
// }


void generateTrapezoidProfile(Profile_param* param, ArrayStruct* profile) {
    if (param == NULL || profile == NULL || param->steps > ARRAY_SIZE) return;

    uint32_t accelSteps = 0;
    uint32_t decelSteps = 0;
    uint32_t flatSteps = 0;

    // Compute the number of steps required to accelerate
    while ((param->lowSpeedInterval - accelSteps * param->accel) > param->highSpeedInterval) {
        accelSteps++;
    }

    decelSteps = accelSteps;
    flatSteps = (param->steps > 2 * accelSteps) ? (param->steps - 2 * accelSteps) : 0;

    profile->size = param->steps;
    uint32_t interval = param->lowSpeedInterval;
    size_t index = 0;

    // Acceleration Phase
    for (; index < accelSteps; index++) {
        interval = param->lowSpeedInterval - (index * param->accel);
        if (interval < param->highSpeedInterval) interval = param->highSpeedInterval;
        profile->data[index] = interval;
    }

    // Constant Speed Phase
    for (size_t i = 0; i < flatSteps; i++, index++) {
        profile->data[index] = param->highSpeedInterval;
    }

    // Deceleration Phase
    for (size_t i = 0; i < decelSteps; i++, index++) {
        interval = param->highSpeedInterval + (i * param->accel);
        if (interval > param->lowSpeedInterval) interval = param->lowSpeedInterval;
        profile->data[index] = interval;
    }
}



int moveMotorTo(ArrayStruct* arr, GPIO_TypeDef *GPIOx, uint32_t pin,runState* state)
{
    uint32_t now= GetUsTime();
    if ((now - state->start_time) >= arr->data[state->index])
    {   state->start_time = GetUsTime();
        if (state->pinstate == 0)
        {
            setPin(GPIOx, pin);
            state->pinstate = 1;
        }
        else
        {
            resetPin(GPIOx, pin);
            state->pinstate = 0;
            state->index++;
        }
    }
    if(state->index > arr->size)
        return 1;
    return 0;
    
}

