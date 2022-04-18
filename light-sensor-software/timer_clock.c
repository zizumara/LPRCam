#include <xc.h>
#include <pic12lf1822.h>
#include "timer_clock.h"

uint32_t TMR0ClockMs = 0;

// Timer0 is configured for the purposes of generating interrupts approximately
// every 1 millisecond.
void init_TMR0(void)
{
    OPTION_REGbits.TMR0CS = 0;  // set timer0 as timer driven by Fosc/4 
    OPTION_REGbits.PSA = 0;     // prescaler assigned to timer0
    OPTION_REGbits.PS = OPTREG_PS;  // select prescale
    TMR0 = 0;                   // initialize TMR0 register
    INTCONbits.TMR0IE = 1;      // enable timer0 interrupts
    INTCONbits.TMR0IF = 0;      // clear timer0 interrupt flag
}

// Update the global 1 millisecond sample clock.
void TMR0_clock_handler(void)
{
    if (INTCONbits.TMR0IF == 1)
    {
        INTCONbits.TMR0IF = 0;
        TMR0ClockMs++;
    }
}

// Returns the current timer0 clock value.
uint32_t TMR0_get_clock(void)
{
    return TMR0ClockMs;
}

// Resets the current timer0 clock value to 0.
void TMR0_reset_clock(void)
{
    TMR0ClockMs = 0;
}