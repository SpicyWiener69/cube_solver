
#include "main.h"



int main(void)
{
  //HAL_Init();

  SystemClock_Config();
  MhzTimer_Init();
  //EXTI_Init();
  //NVIC_Init();
  GPIO_Init();
 
  int i = 1;
  
  while (1)
  {

    
   
    
    // uint32_t lowSpeedInterval = 3000;   // Start at 500µs step interval
    // uint32_t highSpeedInterval = 400;  // Minimum interval at high speed
    // uint32_t accel = 40;               // Acceleration step decrement
    // uint32_t steps = 600;               // Total steps in the profile
    // Profile_param param = {}

    Profile_param param = {
    .lowSpeedInterval = 3000,   // Start at 3000µs step interval
    .highSpeedInterval = 400,   // Minimum interval at high speed
    .accel = 40,                // Acceleration step decrement
    .steps = 600                // Total steps in the profile
    };
    ArrayStruct profile = { .size = 0 };
    generateTrapezoidProfile(&param, &profile);  
    
    ResetUsTimer();
    runState profileState;
    profileState.index = 0;
    profileState.start_time = GetUsTime();
    profileState.pinstate = 0;

    while(1){
      if(moveMotorTo(&profile, GPIOA,5,&profileState))
        break;


    }


  
    //for(int i =0;i<10000000;++i){};
    //HAL_GPIO_TogglePin(GPIOA,GPIO_PIN_5);
    // i = 0;
    // HAL_GPIO_TogglePin(GPIOC,GPIO_PIN_6);
    //HAL_Delay(1000);
   
  }
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
