// File: TMR0_clock.h

#ifndef XC_TMR0_CLOCK_H
#define	XC_TMR0_CLOCK_H

#include <stdint.h>

// Choose system clock and timer0 settings to produce a 1 millisecond period
// for timer0.  For example,
//   If the system clock is 32 MHz,
//   Fosc/4 period @ 32 MHz is 0.125 us per tick,
//   Prescaled by 1:32 yields 4 us per tick,
//   Timer0 8-bit register overflows at 256 * 0.004 ms = 1.024 ms
// NOTE:
// Using the fastest system clock minimizes occasional errors in I2C data 
// transmission at the expense of higher power consumption.

#define _XTAL_FREQ         32000000  // internal oscillator freq for _delay()
#define OSCCON_SCS         0b00      // 0b00 = set src from Config Word 1 FOSC
                                     //    (required for 4x PLL)
                                     // 0b1x = set src to internal oscillator
#define OSCCON_IRCF        0b1110    // select 8 or 32 MHz clock frequency
#define OSCCON_PLL         1         // 1 = 4x PLL on for 32 MHz
                                     // 0 = 4x PLL off for 8 MHz
#define OPTREG_PS          0b100     // 0b100 = 1:32 prescale for timer0
                                     // 0b010 = 1:8 prescale for timer0

void init_TMR0(void);
void TMR0_clock_handler(void);
uint32_t TMR0_get_clock(void);
void TMR0_reset_clock(void);

#endif	// XC_TMR0_CLOCK_H

