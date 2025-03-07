
#include "main.h"



typedef enum{RECEIVE,PARSING, SOLVING,ERR}State;
State state = RECEIVE;

int main(void)
{ 
  // HAL_Init();

  SystemClock_Config();
  MhzTimer_Init();
  // EXTI_Init();
  // NVIC_Init();
  GPIO_Init();
  Uart2_Init();
  CommandStr commands = recieve_bytes_until(1000,'#');
  transmit_bytes(commands);

  //ResetUsTimer();
  // while(1){
  //   if (GetUsTime()>1000000){
  //   
  //   transmit_byte('1');
  //   ResetUsTimer();
  //   } 
  // }
  
  
  Motor_config_T motorLR = initMotorLR();
  Motor_config_T motorD = initMotorD();
  Motor_lst_T motorList = {0};
  motorList.Motor_config[0] = motorLR;
  motorList.Motor_config[1] = motorD;
  motorList.length = 2;

  // char str[] = "A 50; B 60; C -30;";
  // commands.length = strlen(str);
  // strcpy(commands.arr, str);
  
  Task_lst_T task_lst =  parse_string_to_tasks(commands);

  for(int i = 0;i < task_lst.length; ++i){
    ResetUsTimer();
    Task_T task = task_lst.task[i];
    Motor_config_T motor = findMotorById(task.id, motorList);
    ArrayStruct_T profile = generateTrapezoidProfile(task);
    updateTaskProfilePtr(&task, &profile);
    while (1)
      {
        if (moveMotor(motor,task))
          break;
      }
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

  // while (1)
  // {
  //   // runState profileState;
  //   // profileState.index = 0;
  //   // profileState.start_time = GetUsTime();
  //   char* str = "L 90";
  //   Task_T task = parse_string_to_task(str);
  //   Motor_config_T motor = findMotorById(task.id,motorList);
  //   ResetUsTimer();
  //   while (1)
  //     {
  //       if (moveMotor(motor,task))
  //         break;
  //     }
  // }
}

Motor_config_T initMotorLR(void){
  Motor_config_T MotorLR = {
      .id = 'L',
      .GPIO = GPIOA,
      .dirPin = 7,
      .stepPin = 5
      // .lowSpeedInterval = 1000,
      // .highSpeedInterval = 100,
      // .accel = 5,
      // .steps = 4000,
     // ._index = 0,
     // ._pinstate = 0,
    // ._start_time = 0,

  };
  return MotorLR;
}

Motor_config_T initMotorD(void){
  Motor_config_T MotorLR = {
      .id = 'D',
      .GPIO = GPIOA,
      .dirPin = 9,
      .stepPin = 4
      // .lowSpeedInterval = 1000,
      // .highSpeedInterval = 100,
      // .accel = 5,
      // .steps = 4000,
     // ._index = 0,
     // ._pinstate = 0,
    // ._start_time = 0,

  };
  return MotorLR;
}

Motor_config_T findMotorById(uint8_t id, Motor_lst_T lst){
  for (int i = 0; i < lst.length; ++i){
    if (id == lst.Motor_config[i].id){
        return lst.Motor_config[i];
    }
  }
  
}

Task_T init_task(void)
{
  Task_T task = {
    .lowSpeedInterval = 1000,
    .highSpeedInterval = 100,
    .accel = 5,
    ._index = 0,
    ._pinstate = 0,
    ._start_time = 0,
    .stepsPer360 = 400,
  };
  return task;
}

Task_T string_to_task(char* str){
  Task_T task = init_task(); 
  char motorID;
  int32_t deg;
  if (sscanf(str," %c %ld", &motorID, &deg) != 2){
    Error_Handler();
  }
  task.id = motorID;
  task.direction = (deg > 0)? 1: -1;
  task.steps = deg / 360 * task.stepsPer360;
  return task; 
}

Task_lst_T parse_string_to_tasks(CommandStr command_str){
  uint32_t i = 0;
  char * pch;
  Task_lst_T task_lst = {.length = 0,.task = {{0}}};
  pch = strtok(command_str.arr,";");
  while (pch != NULL)
  {
    Task_T task_instance = string_to_task(pch);
    task_lst.task[i] = task_instance;
    pch = strtok (NULL, ";");
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
