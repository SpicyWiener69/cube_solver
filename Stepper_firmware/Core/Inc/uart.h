#ifndef UART_H
#define UART_H

#include "stm32f4xx.h"
#include "gpio_def.h"


void Uart2_Init(void);

char  recieve_byte();
void tx_byte(char txb);

#endif