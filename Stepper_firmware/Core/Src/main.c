
#include "main.h"


StepperMotor initMotorATask(void);

int main(void)
{
  //HAL_Init();

  SystemClock_Config();
  MhzTimer_Init();
  //EXTI_Init();
  //NVIC_Init();
  GPIO_Init();
 
  while (1)
  {

    
   
    
    // uint32_t lowSpeedInterval = 3000;   // Start at 500µs step interval
    // uint32_t highSpeedInterval = 400;  // Minimum interval at high speed
    // uint32_t accel = 40;               // Acceleration step decrement
    // uint32_t steps = 600;               // Total steps in the profile
    // Profile_param param = {}

    // Profile_param param = {
    // .lowSpeedInterval = 3000,   // Start at 3000µs step interval
    // .highSpeedInterval = 400,   // Minimum interval at high speed
    // .accel = 40,                // Acceleration step decrement
    // .steps = 600                // Total steps in the profile
    // };
    // ArrayStruct profile = { .size = 0 };
    // generateTrapezoidProfile(&param, &profile);  
    
    // 
    // runState profileState;
    // profileState.index = 0;
    // profileState.start_time = GetUsTime();
    
    // profileState.pinstate = 0;
    StepperMotor motorA = initMotorATask(); 
    ArrayStruct profile = {.size = 0};
    generateTrapezoidProfile(motorA,&profile);
    motorA.accelProfilePtr = &profile;
    
    ResetUsTimer(); //global us timer , reset  every task
    while(1){
      if(moveMotor(&motorA))
        break;

    }
  }
}

StepperMotor initMotorATask(){
  StepperMotor MotorA = {
    .GPIO = GPIOA,
    .dirPin = 7,
    .stepPin = 5,
    .steps = 4000,
    .accel = 5,
    .lowSpeedInterval = 1000,
    .highSpeedInterval = 100, 
    ._index = 0,
    ._pinstate = 0,
    ._start_time = 0,
    
     };
  return MotorA;
}


void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
