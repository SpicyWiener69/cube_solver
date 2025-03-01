#include "board_init.h"




void SystemClock_Config(void) 
{ /*mco*/
  //RCC->CFGR |= (3<< RCC_CFGR_MCO1_Pos); //PLL clock selected
  //RCC->CFGR |= 0b110 << RCC_CFGR_MCO1PRE_Pos; //mco div by 4

  RCC->CR |= RCC_HSI_ON;
  while (!(RCC->CR & RCC_CR_HSIRDY))
  {
  }; // wait till HSI is ready

  FLASH->ACR |= FLASH_ACR_ICEN | FLASH_ACR_PRFTEN | FLASH_ACR_DCEN | FLASH_ACR_LATENCY_3WS;
  
  /*pll source = HSI*/
  RCC->PLLCFGR |= RCC_PLLCFGR_PLLSRC_HSI;
  /* M = 8, N = 168, P = 4 */
  RCC->PLLCFGR = (8 << RCC_PLLCFGR_PLLM_Pos) | (168 << RCC_PLLCFGR_PLLN_Pos) | (0b01 <<RCC_PLLCFGR_PLLP_Pos);
  // RCC->PLLCFGR |= ;
  // RCC->PLLCFGR |= (0b01 <<RCC_PLLCFGR_PLLP_Pos ); // div by 4
  
  /*enable PLL*/
  RCC->CR |= RCC_CR_PLLON;
  /*select PLL as sysclk*/
  RCC->CFGR |= RCC_CFGR_SW_PLL;
  
  /*config APBx clock divisions*/
  RCC->CFGR |= RCC_CFGR_HPRE_DIV1;
  RCC->CFGR |= RCC_CFGR_PPRE2_DIV1;
  RCC->CFGR |= RCC_CFGR_PPRE1_DIV2;

  
  SystemCoreClockUpdate();
}

// void SystemClock_Config(void)
// {
//   RCC_OscInitTypeDef RCC_OscInitStruct = {0};
//   RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

//   /** Configure the main internal regulator output voltage
//   */
//   __HAL_RCC_PWR_CLK_ENABLE();
//   __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE2);

//   /** Initializes the RCC Oscillators according to the specified parameters
//   * in the RCC_OscInitTypeDef structure.
//   */
//   RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
//   RCC_OscInitStruct.HSEState = RCC_HSE_BYPASS;
//   RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
//   RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
//   RCC_OscInitStruct.PLL.PLLM = 8;
//   RCC_OscInitStruct.PLL.PLLN = 336;
//   RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
//   RCC_OscInitStruct.PLL.PLLQ = 7;
//   if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
//   {
//     Error_Handler();
//   }

//   /** Initializes the CPU, AHB and APB buses clocks
//   */
//   RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
//                               |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
//   RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
//   RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
//   RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
//   RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

//   if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
//   {
//     Error_Handler();
//   }
// }



void EXTI_Init(){
  /*enable SYSCFG on APB2*/
  RCC->APB2ENR |= RCC_APB2ENR_SYSCFGEN;

  /**/
  SYSCFG->EXTICR[BUTTONPIN/4] &= ~(SYSCFG_EXTICR3_EXTI8_Msk);
  SYSCFG->EXTICR[BUTTONPIN/4] |= SYSCFG_EXTICR3_EXTI8_PC;

    /* Setup the button's EXTI line as an interrupt. */
    EXTI->IMR  |=  (1 << BUTTONPIN);
    // Enable the 'rising edge' trigger (button press).
    EXTI->RTSR |=  (1 << BUTTONPIN);

    //EXTI->FTSR |=  (1 << BUTTONPIN);

}

void NVIC_Init(){
  NVIC_SetPriority(EXTI9_5_IRQn, 0x03);
  NVIC_EnableIRQ(EXTI9_5_IRQn);

}


void GPIO_Init(){
  /*enable GPIO clocks*/
  RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
  RCC->AHB1ENR |= RCC_AHB1ENR_GPIOCEN;
  
  /*set GPIOC P8 as input*/
  GPIOC->MODER |=  (GPIO_MODER_INPUT << GPIO_MODER_MODER8_Pos);
 
  /*set GPIOA P5 as output*/ 
  GPIOA->MODER |= (GPIO_MODER_OUTPUT << GPIO_MODER_MODER5_Pos);

  /*set GPIOA P8 as AF*/ 
  GPIOA->MODER |= (GPIO_MODER_ALTERNATE << GPIO_MODER_MODER8_Pos);
  GPIOA->OSPEEDR |= (0b11 << 8*2); 
  /*set AF0*/
  GPIOA->AFR[1] = 0b0000 << GPIO_AFRH_AFRH0;

}

void MhzTimer_Init(void)  
{        
  /*enable TIM2 on APB1, TIM2->CNT = 32bit*/
  RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;
  
  /*counter enable */
  TIM2->CR1 |= TIM_CR1_CEN;

  /*config prescaler*/
  TIM2->PSC |= 84 -1;

  /*update*/
  TIM2->EGR = TIM_EGR_UG;
  

}




// void MX_USART2_UART_Init(void)
// {

//   /* USER CODE BEGIN USART2_Init 0 */

//   /* USER CODE END USART2_Init 0 */

//   /* USER CODE BEGIN USART2_Init 1 */

//   /* USER CODE END USART2_Init 1 */
//   huart2.Instance = USART2;
//   huart2.Init.BaudRate = 115200;
//   huart2.Init.WordLength = UART_WORDLENGTH_8B;
//   huart2.Init.StopBits = UART_STOPBITS_1;
//   huart2.Init.Parity = UART_PARITY_NONE;
//   huart2.Init.Mode = UART_MODE_TX_RX;
//   huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
//   huart2.Init.OverSampling = UART_OVERSAMPLING_16;
//   if (HAL_UART_Init(&huart2) != HAL_OK)
//   {
//     Error_Handler();
//   }
//   /* USER CODE BEGIN USART2_Init 2 */

//   /* USER CODE END USART2_Init 2 */
// }

// void MX_GPIO_Init(void)
// {
//   GPIO_InitTypeDef GPIO_InitStruct = {0};
//   /* USER CODE BEGIN MX_GPIO_Init_1 */
//   /* USER CODE END MX_GPIO_Init_1 */

//   /* GPIO Ports Clock Enable */
//   __HAL_RCC_GPIOC_CLK_ENABLE();
//   __HAL_RCC_GPIOH_CLK_ENABLE();
//   __HAL_RCC_GPIOA_CLK_ENABLE();
//   __HAL_RCC_GPIOB_CLK_ENABLE();

//   /*Configure GPIO pin Output Level */
//   HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET);

//   /*Configure GPIO pin Output Level */
//   HAL_GPIO_WritePin(GPIOC, GPIO_PIN_8, GPIO_PIN_RESET);

//   /*Configure GPIO pin : B1_Pin */
//   GPIO_InitStruct.Pin = B1_Pin;
//   GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
//   GPIO_InitStruct.Pull = GPIO_NOPULL;
//   HAL_GPIO_Init(B1_GPIO_Port, &GPIO_InitStruct);

//   /*Configure GPIO pin : LD2_Pin */
//   GPIO_InitStruct.Pin = LD2_Pin;
//   GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
//   GPIO_InitStruct.Pull = GPIO_NOPULL;
//   GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
//   HAL_GPIO_Init(LD2_GPIO_Port, &GPIO_InitStruct);

//   /*Configure GPIO pin : PC6 */
//   GPIO_InitStruct.Pin = GPIO_PIN_6;
//   GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
//   GPIO_InitStruct.Pull = GPIO_NOPULL;
//   HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

//   /*Configure GPIO pin : PC8 */
//   GPIO_InitStruct.Pin = GPIO_PIN_8;
//   GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
//   GPIO_InitStruct.Pull = GPIO_NOPULL;
//   GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
//   HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

//   /* USER CODE BEGIN MX_GPIO_Init_2 */
//   /* USER CODE END MX_GPIO_Init_2 */
// }