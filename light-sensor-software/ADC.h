
// File: ADC.h

#ifndef XC_ADC_H
#define	XC_ADC_H

#include <stdint.h>

#define ADCON0_CHAN  0b00011     // channel AN3 selection for a PIC12LF1822

void init_ADC(void);
uint16_t read_ADC(void);

#endif	/* ADC_H */

