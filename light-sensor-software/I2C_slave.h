// File: I2C_slave.h

#ifndef XC_I2C_SLAVE_H
#define	XC_I2C_SLAVE_H

#define SSPIDX_AVG_L        0
#define SSPIDX_AVG_H        1
#define SSPIDX_MEAS_L       2
#define SSPIDX_MEAS_H       3
#define SSPIDX_RFRSH_SEC_L  4
#define SSPIDX_RFRSH_SEC_H  5
#define SSPIDX_TRIG_L       6
#define SSPIDX_TRIG_H       7
#define I2C_BUFFERSIZE      8
#define I2C_SLAVE_ADDR      0x30

extern unsigned char SSPBuffer[];

void init_I2C(void);
void I2C_slave_handler(void);

#endif // I2C_SLAVE_H