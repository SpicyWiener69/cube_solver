
#include "servo.h"

/* timer3, channel 3 , C8 pin*/
void servo_Init(void)  
{        
  // /*enable TIM3 on APB1 */
  // RCC->APB1ENR |= RCC_APB1ENR_TIM3EN;
  
  // /*counter enable */
  // TIM3->CR1 |= TIM_CR1_CEN;

  // /*config prescaler , 1Mhz*/
  // TIM3->PSC = 84 -1;
  // /* 1Mhz / 20000 = 50hz */
  // TIM3->ARR  = 20000;
  // /*update*/
  // TIM3->EGR = TIM_EGR_UG;

  // /*initalize port*/

// Enable clocks for GPIO and TIMER4
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIODEN;
    RCC->APB1ENR |= RCC_APB1ENR_TIM4EN;

    // Set alternate function on PD15
    GPIOD->MODER |= GPIO_MODER_MODER15_1;
    GPIOD->AFR[1] |= GPIO_AFRH_AFSEL15_1;

    // Set CC4 channel to output mode (default after reset)
    TIM4->CCMR2 &= ~TIM_CCMR2_CC4S;
    TIM3->CCMR2 &= ~TIM_CCMR2_CC4S;
  
    // Select the polarity by writing the CCxP bit in CCER register.
    TIM4->CCER &= ~TIM_CCER_CC4P;

    // Select the PWM mode (PWM1 or PWM2) by writing OCxM bits in CCMRx register.
    TIM4->CCMR2 |= TIM_CCMR2_OC4M_2 | TIM_CCMR2_OC4M_1;

    // Program the period and the duty cycle respectively in ARR and CCRx registers.
    TIM4->PSC = 15999; // PSC divides the 16MHz clock so it is running the counter at 1kHz
    TIM4->ARR = PERIOD;
    TIM4->CCR4 = DUTY;

    // Set the preload bit in CCMRx register and enable auto-reload preload
    TIM4->CCMR2 |= TIM_CCMR2_OC4PE;
    TIM4->CR1 |= TIM_CR1_ARPE;

} 