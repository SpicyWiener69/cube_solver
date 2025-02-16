
#include "main.h"

Stepper_T initMotor1(void);
//StepperMotor initMotorBTask(void);

int main(void)
{
  // HAL_Init();

  SystemClock_Config();
  MhzTimer_Init();
  // EXTI_Init();
  // NVIC_Init();
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
    Stepper_T motor1 = initMotor1();

    StepperMotor_lst_T StepperMotor_lst = {
      .length = 1,
      .motor[0] = motor1,
      
    };

    Motor_Task_lst_T task_lst = {
        .task[0].direction = 1,
        .task[0].steps = 100,
        .task[0].id = 1,
        .length = 1,
    };

    for (int i = 0; i < StepperMotor_lst.length; ++i){
      for (int j = 0; i < task_lst.length; ++j){
        if(StepperMotor_lst.motor[i].config.id ==task_lst.task[j].id){
          ArrayStruct_T profile = {.size = 0};
          generateTrapezoidProfile(&StepperMotor_lst.motor[i],&profile);
          StepperMotor_lst.motor[i].task.steps = task_lst.task[j].steps;
          StepperMotor_lst.motor[i].task.direction = task_lst.task[j].direction;
        }
    } 

    for (int i = 0; i < task_lst.length; ++i)
    {
      ResetUsTimer(); // global us timer , reset  every task
      while (1)
      {
        if (moveMotor(&motor1))
          break;
      }
    }
  }
}

Stepper_T initMotor1()
{
  Stepper_T MotorA = {
      .config.id = 1,
      .config.GPIO = GPIOA,
      .config.dirPin = 7,
      .config.stepPin = 5,
      .config.lowSpeedInterval = 1000,
      .config.highSpeedInterval = 100,
      config.accel = 5,
      // .steps = 4000,
     // ._index = 0,
     // ._pinstate = 0,
    // ._start_time = 0,

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

#ifdef USE_FULL_ASSERT
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
