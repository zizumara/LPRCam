// File: I2C_slave.c

#include <xc.h>
#include <pic12lf1822.h>
#include "I2C_slave.h"

unsigned char SSPBuffer[I2C_BUFFERSIZE];

// Initialize the I2C module for slave operation.
void init_I2C(void)
{    
    SSP1CON1 = 0b00110110;  // SSPEN enabled, WCOL no collision, SSPOV no overflow,
                            // CKP clock enable, SSPM I2C slave 7-bit
    
    SSP1CON2 = 0b00000000;  // ACKSTAT received, RCEN disabled, RSEN disabled, 
                            // ACKEN disabled, ACKDT acknowledge, GCEN disabled,
                            // PEN disabled, SEN (clock stretch) disabled
    
    SSP1CON3 = 0b00001000;  // BOEN disabled, AHEN disabled, SBCDE disabled, 
                            // SDAHT 300 ns hold, ACKTIM ackseq, DHEN disabled, 
                            // PCIE disabled, SCIE disabled
    
    SSP1STAT = 0x00;        // clear SSP1 status
    SSP1BUF  = 0x00;        // clear SSP1 buffer
    SSP1MSK  = 0xff;        // unmask all address bits
    SSP1ADD  = I2C_SLAVE_ADDR << 1;  // set the slave address
    SSP1IF = 0;             // clear the SSP interrupt flag
    SSP1IE = 1;             // enable SSP interrupts
}

void I2C_slave_handler(void)
{
    static unsigned char byteCount = 0;
    static unsigned char registerIndex = 0;
    unsigned char tempBuf = 0;

    if (SSP1IF == 1)
    {
        SSP1IF = 0;                   // clear SSP interrupt flag
        if (D_nA == 0)
        {
            // Latest received byte is an address.
            byteCount = 0;
            if (BF == 1)
            {
                tempBuf = SSP1BUF;   // clear slave address from buffer
            }

            if (R_nW == 1)
            {
                // R/W bit of address indicates master intends to read.  Load
                // the read data from the latest register offset.
                WCOL = 0;
                if (registerIndex < I2C_BUFFERSIZE)
                {
                    SSP1BUF = SSPBuffer[registerIndex++];
                }
                else
                {
                    SSP1BUF = 0xaa;     // out of bounds
                }
            }
        }
        else
        {
            // Latest received byte is data.
            byteCount++;
            if (BF == 1)
            {
                tempBuf = SSP1BUF;              
            }
            
            if (R_nW == 1)
            {
                // Continuation of multi-byte read.
                WCOL = 0;
                SSP1BUF = SSPBuffer[registerIndex++];
            } 
            else
            {
                // Master is writing data.
                if (byteCount == 1)
                {
                    // The first byte of a write by the master is the 
                    // offset to the location to be written.
                    registerIndex = tempBuf;
                }
                else
                {
                    // Subsequent bytes are data to write to the location.
                    SSPBuffer[registerIndex++] = tempBuf;
                }
            }
        }

        CKP = 1;     // release clock (applies only if SEN = 1)
    }
}
