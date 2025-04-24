
#include "main.h"

typedef enum State
{
	RECEIVE,
	REQUEST_TRANSMIT,
	//PARSING,
	SOLVING,
	//ERR
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
	servo_config_T servo = servo_Init(90);
	
	Motor_config_T motorLR = initMotor('L', GPIOA, 6, 7, 1);
	Motor_config_T motorD = initMotor('D', GPIOB, 4, 5, 1);
	Motor_config_T motorT = initMotor('T', GPIOB, 14, 15, -1);
	Motor_config_T motorC = initMotor('C', GPIOB, 8, 9, 1);

	Motor_lst_T motorList = {0};
	motorList.Motor_config[0] = motorLR;
	motorList.Motor_config[1] = motorD;
	motorList.Motor_config[2] = motorT;
	motorList.Motor_config[3] = motorC;
	motorList.length = 4;
	initStepperGPIO(motorList);

	state = RECEIVE;
	while (1)
	{
		CommandStr commands;
		Task_lst_T task_lst;
		switch (state)
		{
		case RECEIVE:
			commands = recieve_bytes_until('#');
			//transmit_command(commands);
			// task_lst = parse_string_to_tasks(commands);
			// if (!task_lst.parse_success)
			// {
			// 	state = REQUEST_TRANSMIT;
			// 	break;
			// }
			state = SOLVING;
			break;

		case SOLVING:
			char *pch;
			pch = strtok(commands.arr, ";");
			while (pch != NULL){
				Action_T action = parse_string(pch);
				pch = strtok(NULL, ";");
				if(!action.parse_success){
					transmit_byte('$');
					break;
					
				}
			
				if (action.id == 'G')
				{
					servo = moveServoMotorAbs(servo, action.magnitude);
				}
				else if (action.id == 'W'){
					ResetUsTimer();
					/*incoming format = Ms , Ms  * 1000 -> Us */
					while (GetUsTime() < (action.magnitude * 1000)){}  
				}
				else
				{	Task_T task = string_to_task(action.id,action.magnitude);
					ResetUsTimer();
					Motor_config_T motor = findMotorById(task.id, motorList);
					ArrayStruct_T profile = generateTrapezoidProfile(task);
					// if(!profile.success){
					//   state = REQUEST_TRANSMIT;
					//   break;
					// }
					updateTaskProfilePtr(&task, &profile);
					while (1)
					{
						if (moveMotor(motor, &task))
							break;
					}
				}
			}
			transmit_byte('}');
			state = REQUEST_TRANSMIT;
			break;

		case REQUEST_TRANSMIT:
			transmit_byte('>');
			state = RECEIVE;
			break;
		}
	}
}


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

// Task_T init_task(void)
// {
//   Task_T task = {
//       .lowSpeedInterval = 1000,
//       .highSpeedInterval = 500,
//       .accel = 5,
//       ._index = 0,
//       ._pinstate = 0,
//       ._start_time = 0,
//       .stepsPer360 = 1600,
//   };
//   return task;
// }

uint16_t ValidID(char ID)
{
	switch (ID)
	{
	case 'T':
	case 'L':
	case 'D':
	case 'G':
	case 'C':
	case 'W':
		return 1;
	default:
		return 0;
	}
}

Task_T initTaskByMotorID(char motorID)
{
	Task_T task = {
		._index = 0,
		._pinstate = 0,
		._start_time = 0,
	};
	switch (motorID)
	{
	case 'T':
		task.lowSpeedInterval = 430;
		task.highSpeedInterval = 60;
		task.accel = 1;
		task.stepsPer360 = 1600;
		break;
	case 'L':
		task.lowSpeedInterval = 1000;
		task.highSpeedInterval = 500;
		task.accel = 5;
		task.stepsPer360 = 1600;
		break;
	case 'D':
		task.lowSpeedInterval = 1200;
		task.highSpeedInterval = 700;
		task.accel = 5;
		task.stepsPer360 = 200;
		break;
	case 'G':
		task.lowSpeedInterval = 1000;
		task.highSpeedInterval = 500;
		task.accel = 5;
		task.stepsPer360 = 1600;
		break;
	case 'C':
		task.lowSpeedInterval = 800;
		task.highSpeedInterval = 400;
		task.accel = 5;
		task.stepsPer360 = 1600;
		break;
	default:
		// Use default values
		break;
	}

	return task;
}

Action_T parse_string(char* str)
{	Action_T action;
	int32_t magnitude;
	char motorID;
	if (sscanf(str, " %c:%ld", &motorID, &magnitude) != 2)
	{
		action.parse_success = 0;
		return action;
	}
	if (!ValidID(motorID))
	{
		action.parse_success = 0;
		return action;
	}
	action.id = motorID;
	action.magnitude = magnitude;
	action.parse_success = 1;
	return action;
}

Task_T string_to_task(char motorID, int32_t deg)
{
	// Task_T task;
	// char motorID;
	// int32_t deg;
	// if (sscanf(str, " %c:%ld", &motorID, &deg) != 2)
	// {8000
	// 	task.parse_success = 0;
	// 	return task;
	// }
	// if (!ValidMotorID(motorID))
	// {
	// 	task.parse_success = 0;
	// 	return task;
	// }
	Task_T task = initTaskByMotorID(motorID);

	/*servo motor , no deg to steps conversion */
	//task.relative_deg = deg;
	task.id = motorID;
	task.direction = (deg > 0) ? 1 : -1;
	task.steps = abs(deg) / ((float)360) * task.stepsPer360;
	task.parse_success = 1;
	return task;
}

// Task_lst_T parse_string_to_tasks(CommandStr command_str)
// {
// 	uint32_t i = 0;
// 	char *pch;
// 	Task_lst_T task_lst = {.length = 0, .task = {{0}}};
// 	pch = strtok(command_str.arr, ";");
// 	while (pch != NULL)
// 	{
// 		Task_T task_instance = string_to_task(pch);
// 		if (!task_instance.parse_success)
// 		{ // parse error, early return
// 			task_lst.parse_success = 0;
// 			return task_lst;
// 		}
// 		task_lst.task[i] = task_instance;
// 		pch = strtok(NULL, ";");
// 		i++;
// 	}8000
// 	task_lst.length = i;
// 	task_lst.parse_success = 1;
// 	return task_lst;
// }

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
