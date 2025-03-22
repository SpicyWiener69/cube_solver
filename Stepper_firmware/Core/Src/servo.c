
#include "servo.h"

/* Maps 0<->180(deg)  -->  lower_bound <->higher_bound(ccr value). Tuned for MG995 servo */
static uint16_t servo_mapping(int16_t deg)
{
	int16_t lower_bound = 450;
	int16_t higher_bound = 2500;

	uint16_t ccr = ((float)deg / 180.0f) * (higher_bound - lower_bound) + lower_bound;
	return ccr;
}

servo_config_T moveServoMotorAbs(servo_config_T servo, int16_t abs_deg)
{
	abs_deg = (abs_deg > CLAW_CLOSE_ENDPOINT) ? CLAW_CLOSE_ENDPOINT : abs_deg;
	abs_deg = (abs_deg < CLAW_OPEN_ENDPOINT) ? CLAW_OPEN_ENDPOINT : abs_deg;
	servo.abs_deg = abs_deg;
	uint16_t ccr = servo_mapping(abs_deg);
	TIM3->CCR3 = ccr;
	TIM3->EGR = TIM_EGR_UG;
	return servo;
}

servo_config_T moveServoMotorRelative(servo_config_T servo, int16_t relative_deg)
{
	int16_t previous_deg = servo.abs_deg;
	int16_t abs_deg = previous_deg + relative_deg;
	abs_deg = (abs_deg > CLAW_CLOSE_ENDPOINT) ? CLAW_CLOSE_ENDPOINT : abs_deg;
	abs_deg = (abs_deg < CLAW_OPEN_ENDPOINT) ? CLAW_OPEN_ENDPOINT : abs_deg;
	uint16_t ccr = servo_mapping(abs_deg);
	TIM3->CCR3 = ccr;
	TIM3->EGR = TIM_EGR_UG;
	/*update new deg value*/
	servo.abs_deg = abs_deg;
	return servo;
}

/*init to abs position of()*/
servo_config_T servo_Init(int16_t deg)
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

	servo_config_T servo;
	servo.home_deg = deg;
	servo.abs_deg = deg;
	servo.gpio = GPIOC;

	/* timer 3, channel 3 , C8 pin*/

	/*Enable clocks for GPIOC and TIMER3 */
	RCC->AHB1ENR |= RCC_AHB1ENR_GPIOCEN;
	RCC->APB1ENR |= RCC_APB1ENR_TIM3EN;

	// Set alternate function on PC8
	GPIOC->MODER |= GPIO_MODER_ALTERNATE << GPIO_MODER_MODER8_Pos;
	GPIOC->AFR[1] |= 0b0010 << 0;

	// Program the period and the duty cycle respectively in ARR and CCRx registers.
	/* 84M -> 1MHz */
	TIM3->PSC = 84 - 1;

	/* 1Mhz / 20000 = 50hz */
	uint16_t TIM_arr = 20000;
	TIM3->ARR = TIM_arr;

	uint16_t ccr = servo_mapping(servo.home_deg);
	TIM3->CCR3 = ccr;

	// Select the PWM mode (PWM1 or PWM2) by writing OCxM bits in CCMRx register.
	TIM3->CCMR2 |= TIM_CCMR2_OC3M_2 | TIM_CCMR2_OC3M_1;

	// Set the preload bit in CCMRx register and enable auto-reload preload
	TIM3->CCMR2 |= TIM_CCMR2_OC3PE;

	TIM3->CR1 |= TIM_CR1_ARPE;

	// Set CC3 channel to output mode (default after reset)
	TIM3->CCMR2 &= ~TIM_CCMR2_CC3S;

	// Select the polarity by writing the CCxP bit in CCER register.
	TIM3->CCER &= ~TIM_CCER_CC3P;

	TIM3->CCER |= TIM_CCER_CC3E;

	TIM3->EGR = TIM_EGR_UG;

	TIM3->CR1 |= TIM_CR1_CEN;

	return servo;
}