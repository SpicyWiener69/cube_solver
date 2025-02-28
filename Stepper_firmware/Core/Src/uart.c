#include "uart.h"

void uart2_Config(void)
{
    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;
    //todo:gpio setup, af

    //baud  setup 115200


    //UE, TE, RE

}

void recieve_bytes(){


}
