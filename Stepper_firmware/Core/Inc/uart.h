#ifndef UART_H
#define UART_H

#include "stm32f4xx.h"
#include "gpio_def.h"
#include <string.h>

#define MAX_RECEIVE_LENGTH 2000

typedef struct{
    char arr[MAX_RECEIVE_LENGTH];
    uint16_t length;
    uint16_t success;
}CommandStr;

void Uart2_Init(void);
uint8_t recieve_byte(void);

void transmit_command(CommandStr);
void transmit_bytes(char str[], uint16_t length);
void transmit_byte(uint8_t txb);
CommandStr recieve_bytes_until(uint8_t symbol);

#endif