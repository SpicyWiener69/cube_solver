#ifndef UART_H
#define UART_H

#include "stm32f4xx.h"
#include "gpio_def.h"

#define MAX_RECEIVE_LENGTH 200

typedef struct{
    char arr[MAX_RECEIVE_LENGTH];
    uint16_t length;
    uint16_t success;
}CommandStr;

void Uart2_Init(void);
uint8_t recieve_byte(void);
void transmit_byte(uint8_t txb);
CommandStr recieve_bytes_until(uint16_t maxlength, uint8_t symbol);
void transmit_bytes(CommandStr);

#endif