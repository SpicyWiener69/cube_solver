#include "uart.h"

void Uart2_Init(void)
{
    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;

    // Pa2 as alternate
    GPIOA->MODER |= (GPIO_MODER_ALTERNATE << GPIO_MODER_MODER2_Pos);
    // set pa2 as AF7 -> USART2_TX
    GPIOA->AFR[0] |= 0b0111 << (4 * 2);

    // Pa3 as alternate
    GPIOA->MODER |= (GPIO_MODER_ALTERNATE << GPIO_MODER_MODER3_Pos);
    // set pa3 as AF7 -> USART2_RX
    GPIOA->AFR[0] |= 0b0111 << (4 * 3);

    // baud  target: 57600, fclk = APB1Clk, over8 = 0 , USARTDIV = 45.57
    USART2->BRR |= 45 << USART_BRR_DIV_Mantissa_Pos;
    USART2->BRR |= 9 << USART_BRR_DIV_Fraction_Pos; // fraction: 9/16 ~= 0.56

    // UE, TE, RE
    USART2->CR1 |= (USART_CR1_RE | USART_CR1_TE | USART_CR1_UE);
}

void transmit_command(CommandStr command_str)
{
    for (uint32_t i = 0; i < command_str.length; ++i)
    {
        transmit_byte(command_str.arr[i]);
    }
    transmit_byte('#');
}

// void transmit_bytes(char* str, uint32_t len)
// {
//     for (uint32_t i = 0; i < len; ++i)
//     {
//         transmit_byte(command_str.arr[i]);
//     }
//     transmit_byte('#');
// }

void transmit_bytes(char str[], uint16_t length)
{
    for (uint32_t i = 0; i < length; ++i)
    {
        transmit_byte(str[i]);
    }
    transmit_byte('#');
}

void transmit_byte(uint8_t txb)
{
    while (!(USART2->SR & USART_SR_TXE))
    {
    };
    USART2->DR = txb;
}

uint8_t recieve_byte(void)
{
    char rxb = '\0';
    while (!(USART2->SR & USART_SR_RXNE))
    {
    };
    rxb = USART2->DR;
    return rxb;
}

/*blocking function*/

CommandStr recieve_bytes_until(uint8_t symbol)
{
    uint16_t i = 0;
    uint16_t maxlength = MAX_RECEIVE_LENGTH;
    CommandStr command_str = {
        .arr = {0},
        .success = 0,
    };
    while (maxlength > 0)
    {
        uint8_t rxb = recieve_byte();
        if (rxb == symbol)
        {
            command_str.success = 1;
            break;
        }
        
        command_str.arr[i] = rxb;
        i++;
        maxlength--;
        
    }

    command_str.length = i;
    return command_str;
}

// void transmit_bytes(CommandStr string){
//     for(int i = 0; i< CommandStr)

// }
