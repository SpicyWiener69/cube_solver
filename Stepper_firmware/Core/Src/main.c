
#include "main.h"

typedef enum
{
  RECEIVE,
  PARSING,
  SOLVING,
  ERR
} State;
State state = RECEIVE;

int main(void)
{
  SystemClock_Config();
  MhzTimer_Init();
  // EXTI_Init();
  // NVIC_Init();
  // GPIO_Init();
  Uart2_Init();
  servo_config_T  servo = servo_Init();

  // Motor_config_T motorLR = initMotorLR();
  // Motor_config_T motorD = initMotorD();
  // Motor_config_T motorT = initMotorT();
  // Motor_config_T motorC = initMotorC();

  Motor_config_T motorLR = initMotor('L', GPIOA, 6, 7);
  Motor_config_T motorD  = initMotor('D', GPIOB, 4, 5);
  Motor_config_T motorT  = initMotor('T', GPIOB, 14, 15);
  Motor_config_T motorC  = initMotor('C', GPIOB, 8, 9);

  Motor_lst_T motorList = {0};
  motorList.Motor_config[0] = motorLR;
  motorList.Motor_config[1] = motorD;
  motorList.Motor_config[2] = motorT;
  motorList.Motor_config[3] = motorC;
  motorList.length = 4;
  initStepperGPIO(motorList);
  while (1)
  {
    CommandStr commands = recieve_bytes_until(1000, '#');
    transmit_command(commands);

    // ResetUsTimer();
    // while(1){
    //   if (GetUsTime()>1000000){

    //   transmit_byte('q');
    //   transmit_byte('#');

    //   ResetUsTimer();
    //   }
    // }

    // char str[] = "A 50; B 60; C -30;";
    // commands.length = strlen(str);
    // strcpy(commands.arr, str);

    Task_lst_T task_lst = parse_string_to_tasks(commands);

    for (int i = 0; i < task_lst.length; ++i)
    {
      ResetUsTimer();
      Task_T task = task_lst.task[i];
      if (task.id == 'S')
      {
        //moveServoMotor();
      }
      else
      {
        Motor_config_T motor = findMotorById(task.id, motorList);
        ArrayStruct_T profile = generateTrapezoidProfile(task);
        updateTaskProfilePtr(&task, &profile);
        while (1)
        {
          if (moveMotor(motor, &task))
            break;
        }
      }
    }
    transmit_byte('+');
  }

  // while(1){
  //   switch(state){
  //     case RECEIVE:
  //       commands = recieve_bytes_until((uint16_t)MAX_RECEIVE_LENGTH, (uint8_t)'#');
  //       transmit_byte((uint8_t)'2');
  //       state = PARSING;
  //       break;
  //     case PARSING:

  //   }

  // }

}

// Motor_config_T initMotorLR(void)
// {
//   Motor_config_T MotorLR = {
//       .id = 'L',
//       .GPIO = GPIOA,
//       .dirPin = 6,
//       .stepPin = 7};
//   return MotorLR;
// }

// Motor_config_T initMotorD(void)
// {
//   Motor_config_T MotorD = {
//       .id = 'D',
//       .GPIO = GPIOB,
//       .dirPin = 4,
//       .stepPin = 5};
//   return MotorD;
// }

// Motor_config_T initMotorC(void)
// {
//   Motor_config_T MotorC = {
//       .id = 'C',
//       .GPIO = GPIOB,
//       .dirPin = 8,
//       .stepPin = 9};
//   return MotorC;
// }

// Motor_config_T initMotorT(void)
// {
//   Motor_config_T MotorT = {
//       .id = 'T',
//       .GPIO = GPIOB,
//       .dirPin = 14,
//       .stepPin = 15};
//   return MotorT;
// }



Motor_config_T findMotorById(uint8_t id, Motor_lst_T lst)
{
  for (int i = 0; i < lst.length; ++i)
  {
    if (id == lst.Motor_config[i].id)
    {
      return lst.Motor_config[i];
    }
  }
}

Task_T init_task(void)
{
  Task_T task = {
      .lowSpeedInterval = 1000,
      .highSpeedInterval = 500,
      .accel = 5,
      ._index = 0,
      ._pinstate = 0,
      ._start_time = 0,
      .stepsPer360 = 400,
  };
  return task;
}

Task_T string_to_task(char *str)
{
  Task_T task = init_task();
  char motorID;
  int32_t deg;
  if (sscanf(str, " %c:%ld", &motorID, &deg) != 2)
  {
    Error_Handler();
  }
  /*servo motor , no deg to steps conversion */
  task.deg = deg;
  task.id = motorID;
  task.direction = (deg > 0) ? 1 : -1;
  task.steps = abs(deg) / ((float)360) * task.stepsPer360;
  
  return task;
}

Task_lst_T parse_string_to_tasks(CommandStr command_str)
{
  uint32_t i = 0;
  char *pch;
  Task_lst_T task_lst = {.length = 0, .task = {{0}}};
  pch = strtok(command_str.arr, ";");
  while (pch != NULL)
  {
    Task_T task_instance = string_to_task(pch);
    task_lst.task[i] = task_instance;
    pch = strtok(NULL, ";");
    i++;
  }
  task_lst.length = i;
  return task_lst;
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
