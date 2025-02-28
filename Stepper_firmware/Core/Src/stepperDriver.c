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

static inline void setPin(GPIO_TypeDef *GPIOx, uint32_t pin)
{   
    GPIOx->BSRR = 1 << (pin);
}

static inline void resetPin(GPIO_TypeDef *GPIOx, uint32_t pin)
{
    GPIOx->BSRR = 1 << (16 + pin);
}


ArrayStruct_T generateTrapezoidProfile(Task_T task) {
    if (task.steps > ARRAY_SIZE) return;
    ArrayStruct_T profile;
    uint32_t accelSteps = 0;
    uint32_t decelSteps = 0;
    uint32_t flatSteps = 0;

    // Compute the number of steps required to accelerate
    while ((task.lowSpeedInterval - accelSteps * task.accel) > task.highSpeedInterval) {
        accelSteps++;
    }

    decelSteps = accelSteps;
    flatSteps = (task.steps > 2 * accelSteps) ? (task.steps - 2 * accelSteps) : 0;
    profile.size = task.steps;
    uint32_t interval = task.lowSpeedInterval;
    uint32_t index = 0;

    // Acceleration Phase
    for (; index < accelSteps; index++) {
        interval = task.lowSpeedInterval - (index * task.accel);
        if (interval < task.highSpeedInterval) interval = task.highSpeedInterval;
        profile.data[index] = interval;
    }

    // Constant Speed Phase
    for (uint32_t i = 0; i < flatSteps; i++, index++) {
        profile.data[index] = task.highSpeedInterval;
    }

    // Deceleration Phase
    for (uint32_t i = 0; i < decelSteps; i++, index++) {
        interval = task.highSpeedInterval + (i * task.accel);
        if (interval > task.lowSpeedInterval) interval = task.lowSpeedInterval;
        profile.data[index] = interval;
    }
    ///task. = &profile; //
    return profile;
}


uint8_t moveMotor(Motor_config_T motor,Task_T task)
{
    // Set the motor direction based on the current task's direction.
    if (task.direction == 1) {
        setPin(motor.GPIO, motor.dirPin);
    } else if (task.direction == -1){
        resetPin(motor.GPIO, motor.dirPin);
    }

    // Get the current time.
    volatile uint32_t now = GetUsTime();

    // Check if it's time to change the step state according to the acceleration profile.
    if ((now - task._start_time) >= task.profile.data[task._index]) {
        task._start_time = GetUsTime();

        if (task._pinstate == 0) {
            setPin(motor.GPIO, motor.stepPin);
            task._pinstate = 1;
        } else {
            resetPin(motor.GPIO, motor.stepPin);
            task._pinstate = 0;
            task._index++;  // Advance to the next step in the profile.
        }
    }

    // return 1 to indicate completion.
    if (task._index > task.profile.size)
        return 1;

    return 0;
}

void parse_message(char* message, Task_lst_T task_lst){
     

}



// uint8_t moveMotor(Stepper_T* motor)  
// {  
//     if(motor->direction == 1){
//         setPin(motor->GPIO,motor->dirPin);
//     }
//     else{
//         resetPin(motor->GPIO,motor->dirPin);
//     }
//     volatile uint32_t now = GetUsTime();  
//     if ((now - motor->_start_time) >= motor->accelProfilePtr->data[motor->_index])  
//     {  
//         motor->_start_time = GetUsTime();  
//         if (motor->_pinstate == 0)  
//         {  
//             setPin(motor->GPIO, motor->stepPin);  
//             motor->_pinstate = 1;  
//         }  
//         else  
//         {  
//             resetPin(motor->GPIO, motor->stepPin);  
//             motor->_pinstate = 0;  
//             motor->_index++;  
//         }  
//     }  
//     if (motor->_index > motor->accelProfilePtr->size)  
//         return 1;  
//     return 0;  
// }  




