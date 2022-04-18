EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "LPR Camera Wiring Diagram"
Date "2022-04-17"
Rev "1.0"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L project:SENSOR J5
U 1 1 625D00E1
P 8550 3150
F 0 "J5" H 9019 3201 50  0000 L CNN
F 1 "SENSOR" H 9019 3110 50  0000 L CNN
F 2 "" H 8550 3150 50  0001 C CNN
F 3 "" H 8550 3150 50  0001 C CNN
	1    8550 3150
	1    0    0    -1  
$EndComp
$Comp
L project:LED_ARRAY J2
U 1 1 625D0AFE
P 4150 3300
F 0 "J2" H 4217 2885 50  0000 C CNN
F 1 "LED_ARRAY" H 4217 2976 50  0000 C CNN
F 2 "" H 4150 3300 50  0001 C CNN
F 3 "" H 4150 3300 50  0001 C CNN
	1    4150 3300
	-1   0    0    1   
$EndComp
$Comp
L Device:LED D2
U 1 1 625D215C
P 4400 4850
F 0 "D2" V 4439 4732 50  0000 R CNN
F 1 "RUN" V 4348 4732 50  0000 R CNN
F 2 "" H 4400 4850 50  0001 C CNN
F 3 "~" H 4400 4850 50  0001 C CNN
	1    4400 4850
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Barrel_Jack J1
U 1 1 625D2C81
P 4000 1350
F 0 "J1" H 3770 1308 50  0000 R CNN
F 1 "Barrel_Jack" H 3770 1399 50  0000 R CNN
F 2 "" H 4050 1310 50  0001 C CNN
F 3 "~" H 4050 1310 50  0001 C CNN
	1    4000 1350
	1    0    0    -1  
$EndComp
$Comp
L Connector:Raspberry_Pi_2_3 J4
U 1 1 625D35F2
P 6050 3800
F 0 "J4" H 6050 5281 50  0000 C CNN
F 1 "Raspberry_Pi_2_3" H 6050 5190 50  0000 C CNN
F 2 "" H 6050 3800 50  0001 C CNN
F 3 "https://www.raspberrypi.org/documentation/hardware/raspberrypi/schematics/rpi_SCH_3bplus_1p0_reduced.pdf" H 6050 3800 50  0001 C CNN
	1    6050 3800
	1    0    0    -1  
$EndComp
$Comp
L project:RPI_RUN J3
U 1 1 625D9B88
P 5900 6250
F 0 "J3" H 6228 6301 50  0000 L CNN
F 1 "RPI_RUN" H 6228 6210 50  0000 L CNN
F 2 "" H 5900 6250 50  0001 C CNN
F 3 "" H 5900 6250 50  0001 C CNN
	1    5900 6250
	0    -1   -1   0   
$EndComp
$Comp
L Switch:SW_SPST SW1
U 1 1 625D2662
P 5900 6750
F 0 "SW1" H 5900 6985 50  0000 C CNN
F 1 "SW_SPST" H 5900 6894 50  0000 C CNN
F 2 "" H 5900 6750 50  0001 C CNN
F 3 "~" H 5900 6750 50  0001 C CNN
	1    5900 6750
	1    0    0    -1  
$EndComp
Wire Wire Line
	5850 6350 5850 6450
Wire Wire Line
	5850 6450 5600 6450
Wire Wire Line
	5600 6450 5600 6750
Wire Wire Line
	5600 6750 5700 6750
Wire Wire Line
	5950 6350 5950 6450
Wire Wire Line
	5950 6450 6200 6450
Wire Wire Line
	6200 6450 6200 6750
Wire Wire Line
	6200 6750 6100 6750
$Comp
L project:VREG J7
U 1 1 625E11D1
P 8000 1350
F 0 "J7" H 8278 1401 50  0000 L CNN
F 1 "VREG" H 8278 1310 50  0000 L CNN
F 2 "" H 8000 1350 50  0001 C CNN
F 3 "" H 8000 1350 50  0001 C CNN
	1    8000 1350
	1    0    0    -1  
$EndComp
Wire Wire Line
	5850 1550 5850 2500
Wire Wire Line
	4750 5200 5650 5200
Wire Wire Line
	6850 3300 8450 3300
Wire Wire Line
	6850 3200 7300 3200
Wire Wire Line
	7300 3200 7300 3400
Wire Wire Line
	7300 3400 8450 3400
NoConn ~ 8450 2800
NoConn ~ 8450 3000
NoConn ~ 8450 3100
NoConn ~ 8450 3500
Wire Wire Line
	5250 3300 4250 3300
Wire Wire Line
	4300 1450 4750 1450
Wire Wire Line
	7900 1350 5850 1350
Wire Wire Line
	5850 1350 5850 1250
Wire Wire Line
	5850 1250 4600 1250
Wire Wire Line
	4750 1450 4750 3100
Connection ~ 4750 1450
Wire Wire Line
	4750 3200 4250 3200
Connection ~ 4750 3200
Wire Wire Line
	4750 3200 4750 5200
Wire Wire Line
	4250 3100 4750 3100
Connection ~ 4750 3100
Wire Wire Line
	4750 3100 4750 3200
NoConn ~ 7900 1250
NoConn ~ 7900 1150
Wire Wire Line
	5250 4000 4000 4000
$Comp
L Device:R R2
U 1 1 625F93D4
P 4400 4450
F 0 "R2" H 4470 4496 50  0000 L CNN
F 1 "330" H 4470 4405 50  0000 L CNN
F 2 "" V 4330 4450 50  0001 C CNN
F 3 "~" H 4400 4450 50  0001 C CNN
	1    4400 4450
	1    0    0    -1  
$EndComp
Wire Wire Line
	4000 4000 4000 4300
Wire Wire Line
	4000 4600 4000 4700
Wire Wire Line
	4400 4600 4400 4700
Wire Wire Line
	5250 4100 4400 4100
Wire Wire Line
	4400 4100 4400 4300
$Comp
L Device:R R1
U 1 1 625F8F30
P 4000 4450
F 0 "R1" H 4070 4496 50  0000 L CNN
F 1 "330" H 4070 4405 50  0000 L CNN
F 2 "" V 3930 4450 50  0001 C CNN
F 3 "~" H 4000 4450 50  0001 C CNN
	1    4000 4450
	1    0    0    -1  
$EndComp
$Comp
L Device:LED D1
U 1 1 625D1BCF
P 4000 4850
F 0 "D1" V 4050 4750 50  0000 R CNN
F 1 "PROC" V 3950 4750 50  0000 R CNN
F 2 "" H 4000 4850 50  0001 C CNN
F 3 "~" H 4000 4850 50  0001 C CNN
	1    4000 4850
	0    -1   -1   0   
$EndComp
Wire Wire Line
	5650 5200 5650 5100
Wire Wire Line
	4000 5000 4000 5300
Wire Wire Line
	4000 5300 5850 5300
Wire Wire Line
	5850 5300 5850 5100
Wire Wire Line
	4400 5000 4400 5400
Wire Wire Line
	4400 5400 5950 5400
Wire Wire Line
	5950 5400 5950 5100
Wire Wire Line
	4750 1450 7900 1450
Wire Wire Line
	5750 5100 5750 5500
$Comp
L project:CAMERA J6
U 1 1 6260BC78
P 7350 4650
F 0 "J6" H 7728 4701 50  0000 L CNN
F 1 "CAMERA" H 7728 4610 50  0000 L CNN
F 2 "" H 7350 4650 50  0001 C CNN
F 3 "" H 7350 4650 50  0001 C CNN
	1    7350 4650
	1    0    0    -1  
$EndComp
Wire Wire Line
	6850 4600 7250 4600
Wire Wire Line
	6250 5200 6250 5100
Wire Wire Line
	4600 1250 4600 3400
Wire Wire Line
	4600 3400 4250 3400
Connection ~ 4600 1250
Wire Wire Line
	4600 1250 4300 1250
Wire Wire Line
	4600 3400 4600 3500
Wire Wire Line
	4600 3500 4250 3500
Connection ~ 4600 3400
Text Label 4350 1250 0    50   ~ 0
12V
Text Label 4350 1450 0    50   ~ 0
GND
Text Label 7700 1550 0    50   ~ 0
5V
Text Label 7700 1350 0    50   ~ 0
12V
Wire Wire Line
	5850 1550 7900 1550
Wire Wire Line
	5950 2500 5950 2200
Wire Wire Line
	5950 2200 7500 2200
Wire Wire Line
	7500 2200 7500 2900
Wire Wire Line
	7500 2900 8450 2900
NoConn ~ 6250 2500
NoConn ~ 6150 2500
NoConn ~ 5250 2900
NoConn ~ 5250 3000
NoConn ~ 5250 3200
NoConn ~ 5250 3400
NoConn ~ 5250 3600
NoConn ~ 5250 3700
NoConn ~ 5250 3800
NoConn ~ 6850 2900
NoConn ~ 6850 3000
NoConn ~ 6850 3500
NoConn ~ 6850 3600
NoConn ~ 6850 3700
NoConn ~ 6850 3900
NoConn ~ 6850 4000
NoConn ~ 6850 4100
NoConn ~ 6850 4200
NoConn ~ 6850 4300
NoConn ~ 6850 4500
NoConn ~ 6350 5100
NoConn ~ 6150 5100
NoConn ~ 6050 5100
NoConn ~ 5250 4500
NoConn ~ 5250 4400
NoConn ~ 5250 4300
NoConn ~ 5250 4200
Wire Wire Line
	7250 4700 7150 4700
Wire Wire Line
	7150 4700 7150 5200
Wire Wire Line
	7150 5200 6250 5200
Wire Wire Line
	8350 3200 8350 5500
Wire Wire Line
	5750 5500 8350 5500
Wire Wire Line
	8350 3200 8450 3200
$EndSCHEMATC
