/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
//#include "stm32f4xx_hal.h"
#include "board_init.h"
#include "stm32f4xx_it.h"
#include "stepperDriver.h"
#include "uart.h"
#include "servo.h"

#include<stdlib.h>
#include <stdio.h>
#include <string.h>

typedef struct action{
	char id;
	int32_t magnitude;
	int32_t parse_success;
} Action_T;

void SystemClock_Config(void);
void EXTI_Init(void);
void NVIC_Init(void);
void GPIO_Init(void);
void Error_Handler(void);

Motor_config_T initMotorLR(void);
Motor_config_T initMotorD(void);
Motor_config_T initMotorT(void);
Motor_config_T initMotorC(void);

Action_T parse_string(char* str);
Task_T string_to_task(char motorID, int32_t deg);
//Task_lst_T parse_string_to_tasks(CommandStr command_str);
uint16_t ValidID(char motorID);
Task_T initTaskByMotorID(char motorID);
Motor_config_T findMotorById(uint8_t id, Motor_lst_T lst);

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H  */
