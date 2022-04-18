// File: ADC.c
// Implements functions to initialize the ADC module and read a single ADC
// channel.

#include <xc.h>
#include <pic12lf1822.h>
#include "timer_clock.h"
#include "ADC.h"

uint16_t read_ADC(void)
{
    uint16_t adc_sample = 0;
    
    // Sample the ADC, allowing some time for ADC setup.
    __delay_us(20);
    ADCON0bits.GO = 1;
    while(ADCON0bits.GO_nDONE);
    adc_sample = ADRES;
    return adc_sample;
}

void init_ADC(void)
{
    ADCON1bits.ADCS = 0b010;      // with 32 MHz Fosc, Fosc/32 yields 1 us Tad;
                                  //    ADC conv time = 11.5 x Tad = 11.5 us
    ADCON1bits.ADFM = 1;          // right justified format (2 MS bits in ADRESH)
    ADCON1bits.ADPREF = 0b00;     // Vref+ is Vdd
    ADCON0bits.CHS = ADCON0_CHAN; // select channel
    
    ADCON0bits.ADON = 1;          // enable ADC module
    PIE1bits.ADIE = 0;            // disable ADC interrupts (flag will be polled)
    PIR1bits.ADIF = 0;            // clear ADC interrupt flag
}
