
#include "servo.h"


/* 0<->180  => 1000<->2000  */
static uint32_t servo_mapping(float deg) {
  uint32_t ccr = (deg/180) *  1000 + 1000;
  return ccr;
}

servo_config_T servo_Init(void)  
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

  servo_config_T config;
  /* timer 3, channel 3 , C8 pin*/

  /*Enable clocks for GPIOC and TIMER3 */
  RCC->AHB1ENR |= RCC_AHB1ENR_GPIOCEN;
  RCC->APB1ENR |= RCC_APB1ENR_TIM3EN;

  // Set alternate function on PC8
  GPIOC->MODER |= GPIO_MODER_ALTERNATE << GPIO_MODER_MODER8_Pos;
  GPIOC->AFR[1] |= 0b0010 << 0;

  // Set CC3 channel to output mode (default after reset)
  TIM3->CCMR2 &= ~TIM_CCMR2_CC3S;

  // Select the polarity by writing the CCxP bit in CCER register.
  TIM3->CCER &= ~TIM_CCER_CC3P;

  // Select the PWM mode (PWM1 or PWM2) by writing OCxM bits in CCMRx register.
  TIM3->CCMR2 |= TIM_CCMR2_OC4M_2 | TIM_CCMR2_OC4M_1;

  // Program the period and the duty cycle respectively in ARR and CCRx registers.
  /* 84M -> 1MHz */
  TIM3->PSC = 84 - 1; 
    /* 1Mhz / 20000 = 50hz */
  //uint16_t TIM_arr = 20000; 
  TIM3->ARR  = 20000;
  //ccr = servo_mapping(config.home_deg)
  TIM3->CCR3 = 10000;


  // Set the preload bit in CCMRx register and enable auto-reload preload
  TIM3->CCMR2 |= TIM_CCMR2_OC3PE;
  TIM3->CR1 |= TIM_CR1_ARPE;

  return config;
} 