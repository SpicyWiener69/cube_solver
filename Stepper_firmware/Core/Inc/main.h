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

#include<stdlib.h>
#include <stdio.h>
#include <string.h>

void SystemClock_Config(void);
void EXTI_Init(void);
void NVIC_Init(void);
void GPIO_Init(void);
void Error_Handler(void);

Motor_config_T initMotorLR(void);
Motor_config_T initMotorD(void);
Motor_config_T initMotorT(void);

Task_T parse_string_to_task(char* str);
Task_lst_T parse_string_to_tasks(CommandStr command_str);
Motor_config_T findMotorById(uint8_t id, Motor_lst_T lst);

// #define B1_Pin GPIO_PIN_13
// #define B1_GPIO_Port GPIOC
// #define USART_TX_Pin GPIO_PIN_2
// #define USART_TX_GPIO_Port GPIOA
// #define USART_RX_Pin GPIO_PIN_3
// #define USART_RX_GPIO_Port GPIOA
// #define LD2_Pin GPIO_PIN_5
// #define LD2_GPIO_Port GPIOA
// #define TMS_Pin GPIO_PIN_13
// #define TMS_GPIO_Port GPIOA
// #define TCK_Pin GPIO_PIN_14
// #define TCK_GPIO_Port GPIOA
// #define SWO_Pin GPIO_PIN_3
// #define SWO_GPIO_Port GPIOB



#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
