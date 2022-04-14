EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L MCU_Microchip_PIC12:PIC12LF1822-ISN U1
U 1 1 608C5CBF
P 5400 3550
F 0 "U1" H 5800 4150 50  0000 C CNN
F 1 "PIC12LF1822-ISN" H 5800 4050 50  0000 C CNN
F 2 "custom-footprints:pic12lf1822-i&slash_sn" H 6000 4200 50  0001 C CNN
F 3 "http://ww1.microchip.com/downloads/en/DeviceDoc/41413B.pdf" H 5400 3550 50  0001 C CNN
	1    5400 3550
	1    0    0    -1  
$EndComp
Wire Wire Line
	4400 2850 5400 2850
Wire Wire Line
	5400 2850 5400 2950
$Comp
L Device:R R1
U 1 1 608CC393
P 4300 5050
F 0 "R1" V 4200 5000 50  0000 L CNN
F 1 "10k" V 4300 5000 50  0000 L CNN
F 2 "Resistor_SMD:R_0805_2012Metric_Pad1.15x1.40mm_HandSolder" V 4230 5050 50  0001 C CNN
F 3 "~" H 4300 5050 50  0001 C CNN
	1    4300 5050
	1    0    0    -1  
$EndComp
Wire Wire Line
	4300 5500 4300 5200
Connection ~ 4500 5400
Wire Wire Line
	4500 5400 4500 5500
Wire Wire Line
	4500 5400 4200 5400
Wire Wire Line
	4200 5400 4200 5500
Wire Wire Line
	4800 3550 4000 3550
Wire Wire Line
	4000 3550 4000 5500
Wire Wire Line
	4800 3650 3900 3650
Wire Wire Line
	3900 3650 3900 5500
Wire Wire Line
	3800 5500 3800 3450
Wire Wire Line
	3800 3450 4800 3450
NoConn ~ 6000 3650
$Comp
L Device:R R2
U 1 1 608D46C7
P 6700 3200
F 0 "R2" V 6600 3200 50  0000 C CNN
F 1 "5.1k" V 6700 3200 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric_Pad1.15x1.40mm_HandSolder" V 6630 3200 50  0001 C CNN
F 3 "~" H 6700 3200 50  0001 C CNN
	1    6700 3200
	1    0    0    -1  
$EndComp
Wire Wire Line
	5400 2850 6700 2850
Wire Wire Line
	6700 2850 6700 3050
Connection ~ 5400 2850
$Comp
L Device:R R3
U 1 1 608D6C4F
P 6700 4000
F 0 "R3" V 6600 3950 50  0000 L CNN
F 1 "8.2k" V 6700 3900 50  0000 L CNN
F 2 "Resistor_SMD:R_0805_2012Metric_Pad1.15x1.40mm_HandSolder" V 6630 4000 50  0001 C CNN
F 3 "~" H 6700 4000 50  0001 C CNN
	1    6700 4000
	1    0    0    -1  
$EndComp
Wire Wire Line
	6700 3350 6700 3550
Connection ~ 6700 3550
Wire Wire Line
	6700 3550 6700 3850
$Comp
L Device:R_PHOTO R4
U 1 1 608D8998
P 7200 4000
F 0 "R4" H 7270 4046 50  0000 L CNN
F 1 "R_PHOTO" H 7270 3955 50  0000 L CNN
F 2 "OptoDevice:R_LDR_7x6mm_P5.1mm_Vertical" V 7250 3750 50  0001 L CNN
F 3 "~" H 7200 3950 50  0001 C CNN
	1    7200 4000
	1    0    0    -1  
$EndComp
Wire Wire Line
	6700 3550 7200 3550
Wire Wire Line
	7200 3550 7200 3850
$Comp
L light-sensor-I2C-rescue:PROG_PWR-project J1
U 1 1 608DCB8A
P 4150 5600
F 0 "J1" V 4266 6038 50  0000 L CNN
F 1 "PROG_PWR" V 4357 6038 50  0000 L CNN
F 2 "Connector_PinSocket_2.54mm:PinSocket_2x04_P2.54mm_Horizontal" H 4150 5600 50  0001 C CNN
F 3 "" H 4150 5600 50  0001 C CNN
	1    4150 5600
	0    1    1    0   
$EndComp
Wire Wire Line
	6000 3550 6700 3550
Wire Wire Line
	4100 4500 4600 4500
Wire Wire Line
	7200 4500 7200 4150
Wire Wire Line
	4100 4500 4100 5500
Wire Wire Line
	6700 4150 6700 4500
Connection ~ 6700 4500
Wire Wire Line
	6700 4500 7200 4500
Connection ~ 5400 4500
Wire Wire Line
	5400 4500 6700 4500
Wire Wire Line
	4400 2850 4400 3900
Wire Wire Line
	4300 4900 4300 4700
Wire Wire Line
	4300 4700 4400 4700
Connection ~ 4400 4700
Wire Wire Line
	4400 4700 4400 5100
$Comp
L power:VPP #PWR03
U 1 1 608E1878
P 5400 5250
F 0 "#PWR03" H 5400 5100 50  0001 C CNN
F 1 "VPP" H 5415 5423 50  0000 C CNN
F 2 "" H 5400 5250 50  0001 C CNN
F 3 "" H 5400 5250 50  0001 C CNN
	1    5400 5250
	1    0    0    -1  
$EndComp
$Comp
L power:PWR_FLAG #FLG02
U 1 1 608E2C11
P 5050 4950
F 0 "#FLG02" H 5050 5025 50  0001 C CNN
F 1 "PWR_FLAG" H 5050 5123 50  0000 C CNN
F 2 "" H 5050 4950 50  0001 C CNN
F 3 "~" H 5050 4950 50  0001 C CNN
	1    5050 4950
	1    0    0    -1  
$EndComp
Wire Wire Line
	4500 5400 5400 5400
$Comp
L power:VCC #PWR01
U 1 1 608E47A2
P 4700 4950
F 0 "#PWR01" H 4700 4800 50  0001 C CNN
F 1 "VCC" H 4715 5123 50  0000 C CNN
F 2 "" H 4700 4950 50  0001 C CNN
F 3 "" H 4700 4950 50  0001 C CNN
	1    4700 4950
	1    0    0    -1  
$EndComp
Wire Wire Line
	4700 4950 4700 5100
Wire Wire Line
	5050 4950 5050 5100
Wire Wire Line
	5400 5250 5400 5400
Connection ~ 5400 5400
$Comp
L power:GND #PWR02
U 1 1 608E72F1
P 5400 4700
F 0 "#PWR02" H 5400 4450 50  0001 C CNN
F 1 "GND" H 5405 4527 50  0000 C CNN
F 2 "" H 5400 4700 50  0001 C CNN
F 3 "" H 5400 4700 50  0001 C CNN
	1    5400 4700
	1    0    0    -1  
$EndComp
Wire Wire Line
	5400 4150 5400 4500
Wire Wire Line
	5400 4700 5400 4500
$Comp
L power:PWR_FLAG #FLG01
U 1 1 608EAE15
P 5100 4400
F 0 "#FLG01" H 5100 4475 50  0001 C CNN
F 1 "PWR_FLAG" H 5100 4573 50  0000 C CNN
F 2 "" H 5100 4400 50  0001 C CNN
F 3 "~" H 5100 4400 50  0001 C CNN
	1    5100 4400
	1    0    0    -1  
$EndComp
Text Notes 7000 3400 0    50   ~ 0
R2 and R3 form a voltage divider circuit designed to limit \nthe maximum voltage at RA4 to 2.048 V, which is the \nhighest voltage that the PIC ADC module can measure.  \nAssuming Vdd is 3.3 V, the value of R2 is determined by \nsolving the formula 2.048 / 3.3 = R2 / 8.2k for R2, which \nproduces a value of 5.089k.  A standard 5.1k SMD \nresistor is sufficiently close to the desired value.  The \nphotoresistor should vary from around 500K down to \nless than 200 Ohms.
Text Notes 3000 6650 0    50   ~ 0
The PROG_PWR connector is used alternately for programming \nthe PIC or for normal operation.  During programming, pins J1 \nand J2 are connected together externally to route Vpp to Vcc \nthrough the 10k resistor.  During normal operation, pins J1 and \nJ2 are left unconnected.  Note that no pullup resistors are \nprovided on the I2C SDA and SCL pins, so pullup resistors must \nbe provided by the I2C master.
Text Label 4600 3650 0    50   ~ 0
SDA
Text Label 4600 3550 0    50   ~ 0
SCL
Text Label 4600 3450 0    50   ~ 0
Trig
Text Label 4150 3450 0    50   ~ 0
Pda
Text Label 4150 3550 0    50   ~ 0
Pcl
Wire Wire Line
	6350 5400 6350 3450
Wire Wire Line
	6000 3450 6350 3450
Wire Wire Line
	5400 5400 6350 5400
Text Label 6100 3550 0    50   ~ 0
Meas
Wire Wire Line
	4400 5100 4700 5100
Connection ~ 4400 5100
Connection ~ 4700 5100
Wire Wire Line
	4700 5100 5050 5100
Wire Wire Line
	4400 5100 4400 5500
$Comp
L Device:C C1
U 1 1 608CAEBD
P 4600 4200
F 0 "C1" H 4650 4300 50  0000 L CNN
F 1 "0.1uF" H 4650 4100 50  0000 L CNN
F 2 "Capacitor_SMD:C_0805_2012Metric_Pad1.15x1.40mm_HandSolder" H 4638 4050 50  0001 C CNN
F 3 "~" H 4600 4200 50  0001 C CNN
	1    4600 4200
	1    0    0    -1  
$EndComp
Wire Wire Line
	4600 4500 4600 4350
Connection ~ 4600 4500
Wire Wire Line
	4600 4050 4600 3900
Wire Wire Line
	4600 3900 4400 3900
Connection ~ 4400 3900
Wire Wire Line
	4400 3900 4400 4700
Wire Wire Line
	4600 4500 5100 4500
Wire Wire Line
	5100 4400 5100 4500
Connection ~ 5100 4500
Wire Wire Line
	5100 4500 5400 4500
$EndSCHEMATC
