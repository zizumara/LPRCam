/*******************************************************************************
 * Light Sensor with I2C Interface
 * Created May 9, 2021
 * 
 * Overview:
 * This program runs on a PIC12LF1822 MCU and takes regular ADC samples of the
 * voltage across a CdS photocell, providing the readings across an I2C 
 * interface.  The circuit is designed such that complete darkness reads as
 * near the maximum ADC voltage of 2.048V and full brightness reads near 0V
 * (corresponding to 10-bit values of 1023 and 0, respectively).  The readings
 * are averaged on a sliding window basis, with the time width of the window
 * in seconds specified by the I2C master.  The time width of the window is
 * the amount of time that it takes for all prior measurements to be replaced
 * with new measurements.  The PIC provides a digital output that is set to 
 * high when a measurement level is equaled or exceeded.  The trigger level 
 * may be set by the I2C master.  All values communicated via the I2C 
 * interface occupy 2 bytes each in little endian order.  (Refer to I2C_slave.h
 * for I2C address and buffer offsets.)
 * 
 * Pin assignments: 
 *                                                                    weak
 *    function                           I/O   pin#  in/out  dig/ana  pullup
 * ----------------------------------------------------------------------------
 *    ICSPDAT/level trigger              RA0    7    output  digital  disabled
 *    ICSPCLK/I2C SCL                    RA1    6    input   digital  disabled
 *    I2C SDA                            RA2    5    input   digital  disabled
 *    MCLR/unused                        RA3    4    output  digital  disabled
 *    ADC measurement                    RA4    3    input   analog   disabled
 *    unused                             RA5    2    output  digital  disabled
 * 
 * Modules used:
 *    MSSP (I2C)
 *    ADC
 *    TIMER0
 */

// PIC12LF1822 Configuration Bit Settings
#pragma config FOSC = INTOSC    // Oscillator Selection (INTOSC oscillator: I/O function on CLKIN pin)
#pragma config WDTE = OFF       // Watchdog Timer Enable (WDT disabled)
#pragma config PWRTE = OFF      // Power-up Timer Enable (PWRT disabled)
#pragma config MCLRE = OFF      // MCLR Pin Function Select (MCLR/VPP pin function is digital input)
#pragma config CP = OFF         // Flash Program Memory Code Protection (Program memory code protection is disabled)
#pragma config CPD = OFF        // Data Memory Code Protection (Data memory code protection is disabled)
#pragma config BOREN = ON       // Brown-out Reset Enable (Brown-out Reset enabled)
#pragma config CLKOUTEN = OFF   // Clock Out Enable (CLKOUT function is disabled. I/O or oscillator function on the CLKOUT pin)
#pragma config IESO = OFF       // Internal/External Switchover (Internal/External Switchover mode is disabled)
#pragma config FCMEN = OFF      // Fail-Safe Clock Monitor Enable (Fail-Safe Clock Monitor is disabled)
#pragma config WRT = OFF        // Flash Memory Self-Write Protection (Write protection off)
#pragma config PLLEN = ON       // PLL Enable (4x PLL enabled)
#pragma config STVREN = ON      // Stack Overflow/Underflow Reset Enable (Stack Overflow or Underflow will cause a Reset)
#pragma config BORV = LO        // Brown-out Reset Voltage Selection (Brown-out Reset Voltage (Vbor), low trip point selected.)
#pragma config LVP = OFF        // Low-Voltage Programming Enable (High-voltage on MCLR/VPP must be used for programming)

#include <xc.h>
#include <pic12lf1822.h>
#include <stdint.h>
#include "timer_clock.h"
#include "I2C_slave.h"
#include "ADC.h"

#define NUM_SAMPLES        25    // number of samples in sliding average buffer
#define RFRSH_TO_SAMPLE_MS 41    // approximate number of milliseconds
                                 //   between samples to achieve refresh of 
                                 //   all samples in the sample buffer in 
                                 //   one second
// NOTE: NUM_SAMPLES * RFRSH_TO_SAMPLE_MS should be close to 1024.  This is 
//       because the sample clock period is 1.024 ms, and this allows the
//       sample refresh interval specified by the I2C master to accurately 
//       reflect the time to replace all samples in the sample buffer.

#define LEVEL_TRIGGER      LATAbits.LATA0

// Global data
uint16_t sampleBuffer[NUM_SAMPLES];
uint32_t sampleIntervalMs = RFRSH_TO_SAMPLE_MS;
uint32_t sampleSum = 0;
uint16_t triggerLevel = 0;

// Function prototypes
void sample_ADC(void);

// Interrupt handler wrapper
void __interrupt() main_ISR(void)
{
    I2C_slave_handler();
    TMR0_clock_handler();
}

void main(void)
{
    // Initialize system oscillator.
    OSCCONbits.SCS = OSCCON_SCS;     // Select clock source
    OSCCONbits.IRCF = OSCCON_IRCF;   // Select clock frequency
    OSCCONbits.SPLLEN = OSCCON_PLL;  // Set 4x PLL according to desired freq
    
    // Initialize port bits.
    WPUA   = 0b00000000;      // Disable all weak pull-ups (I2C master to 
                              // provide pull-ups on RA1 & RA2 I2C inputs)
    TRISA  = 0b00010110;      // Set RA0 as output for light level trigger
                              // Set RA1 & RA2 as inputs for I2C (SCL and SDA)
                              // Set RA3 & RA5 as unused outputs
                              // Set RA4 as input for ADC measurement
    ANSELA = 0b00010000;      // Set RA4 as analog for ADC measurement
                              // Set all others to digital
    LEVEL_TRIGGER = 0;        // set light level trigger to not triggered
    init_I2C();               // initialize and enable I2C interface
    init_ADC();               // initialize and enable ADC interface
    init_TMR0();              // initialize timer0 for sampling
    
    INTCONbits.PEIE = 1;      // enable peripheral interrupts
    INTCONbits.GIE  = 1;      // enable global interrupts
    
    
    // Initialize sample buffer and report first measurement.
    __delay_ms(100);          // extra setup time before 1st ADC read
    uint16_t sample1 = read_ADC();
    SSPBuffer[SSPIDX_MEAS_L] = sample1 & 0x00ff;
    SSPBuffer[SSPIDX_MEAS_H] = sample1 >> 8;
    SSPBuffer[SSPIDX_AVG_L] = sample1 & 0x00ff;
    SSPBuffer[SSPIDX_AVG_H] = sample1 >> 8;
    for (int i = 0; i < NUM_SAMPLES; i++)
    {
        sampleBuffer[i] = sample1;
        sampleSum += sample1;
    }
    
    // Set default trigger level to 511 and default refresh interval to 1 sec.
    uint16_t sampleRefreshSecReq = 1;
    SSPBuffer[SSPIDX_RFRSH_SEC_L] = 0x01;
    SSPBuffer[SSPIDX_RFRSH_SEC_H] = 0x00;
    triggerLevel = 511;
    SSPBuffer[SSPIDX_TRIG_L] = 0xff;
    SSPBuffer[SSPIDX_TRIG_H] = 0x01;

    while(1)
    {
        // When the sample clock expires, update the sample buffer with another 
        // ADC sample and restart the clock.
        if (TMR0_get_clock() > sampleIntervalMs)
        {
            TMR0_reset_clock();
            sample_ADC();
        }
        
        // Continuously check for I2C master updates to the sample refresh 
        // interval.  The requested value is in seconds.  Convert it to 
        // milliseconds for use with the sample clock.
        sampleRefreshSecReq = SSPBuffer[SSPIDX_RFRSH_SEC_H];
        sampleRefreshSecReq = (sampleRefreshSecReq << 8) + 
                              SSPBuffer[SSPIDX_RFRSH_SEC_L];
        if (sampleRefreshSecReq == 0)
        {
            sampleIntervalMs = RFRSH_TO_SAMPLE_MS;
        }
        else
        {
            sampleIntervalMs = RFRSH_TO_SAMPLE_MS * sampleRefreshSecReq;
        }
        
        // Continuously check for I2C master updates to the trigger level.
        triggerLevel = SSPBuffer[SSPIDX_TRIG_H];
        triggerLevel = (triggerLevel << 8) + SSPBuffer[SSPIDX_TRIG_L];
    }
}

// This function implements a sliding window summation of all ADC values read.
// On each call, read a new sample value from the ADC, subtract the oldest 
// sample value from the sum of all samples, and add the new sample value to 
// the sample sum, and replace the old sample in the sample buffer with the new
// sample.  This technique avoids having to add up all the sample values to 
// calculate an average every time a new sample is taken.  The average sample 
// value is calculated and written to the SSP buffer along with the current 
// sample value for collection by the I2C master.  The average is also compared
// to the trigger level set by the I2C master in the SSP buffer and the level 
// trigger output is set or cleared based on the comparison.
void sample_ADC(void)
{
    static uint8_t sampleIndex = 0;
    uint16_t newSample = 0;
    uint16_t triggerLevel = 0;
    uint16_t sampleAvg = 0;

    newSample = read_ADC();
    sampleSum -= sampleBuffer[sampleIndex];
    sampleSum += newSample;
    sampleBuffer[sampleIndex] = newSample;
    sampleIndex++;
    if (sampleIndex >= NUM_SAMPLES)
    {
        sampleIndex = 0;
    }
    sampleAvg = sampleSum / NUM_SAMPLES;
    triggerLevel = ((uint16_t)SSPBuffer[SSPIDX_TRIG_H] << 8)
                   + (uint16_t)SSPBuffer[SSPIDX_TRIG_L];
    if (sampleAvg >= triggerLevel)
    {
        LEVEL_TRIGGER = 1;
    }
    else
    {
        LEVEL_TRIGGER = 0;
    }
    SSPBuffer[SSPIDX_AVG_L] = sampleAvg & 0x00ff;
    SSPBuffer[SSPIDX_AVG_H] = sampleAvg >> 8;
    SSPBuffer[SSPIDX_MEAS_L] = newSample & 0x00ff;
    SSPBuffer[SSPIDX_MEAS_H] = newSample >> 8;
}


