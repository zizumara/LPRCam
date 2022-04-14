EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr USLetter 11000 8500
encoding utf-8
Sheet 1 1
Title "28 Infrared LED Driver"
Date "2021-04-15"
Rev "1.0"
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Device:R R4
U 1 1 600C3559
P 3450 3700
F 0 "R4" V 3550 3650 50  0000 L CNN
F 1 "10" V 3450 3650 50  0000 L CNN
F 2 "Resistor_SMD:R_0805_2012Metric_Pad1.15x1.40mm_HandSolder" V 3380 3700 50  0001 C CNN
F 3 "~" H 3450 3700 50  0001 C CNN
	1    3450 3700
	0    -1   -1   0   
$EndComp
$Comp
L power:+12V #PWR03
U 1 1 600D40A3
P 1900 4350
F 0 "#PWR03" H 1900 4200 50  0001 C CNN
F 1 "+12V" H 1915 4523 50  0000 C CNN
F 2 "" H 1900 4350 50  0001 C CNN
F 3 "" H 1900 4350 50  0001 C CNN
	1    1900 4350
	1    0    0    -1  
$EndComp
$Comp
L power:PWR_FLAG #FLG03
U 1 1 600D4737
P 2300 4350
F 0 "#FLG03" H 2300 4425 50  0001 C CNN
F 1 "PWR_FLAG" H 2300 4523 50  0000 C CNN
F 2 "" H 2300 4350 50  0001 C CNN
F 3 "~" H 2300 4350 50  0001 C CNN
	1    2300 4350
	1    0    0    -1  
$EndComp
$Comp
L Device:R R3
U 1 1 600D7E3D
P 3850 5750
F 0 "R3" V 3750 5750 50  0000 C CNN
F 1 "100" V 3850 5750 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric_Pad1.15x1.40mm_HandSolder" V 3780 5750 50  0001 C CNN
F 3 "~" H 3850 5750 50  0001 C CNN
	1    3850 5750
	0    1    1    0   
$EndComp
$Comp
L power:PWR_FLAG #FLG02
U 1 1 600D9842
P 2350 6500
F 0 "#FLG02" H 2350 6575 50  0001 C CNN
F 1 "PWR_FLAG" H 2350 6673 50  0000 C CNN
F 2 "" H 2350 6500 50  0001 C CNN
F 3 "~" H 2350 6500 50  0001 C CNN
	1    2350 6500
	1    0    0    -1  
$EndComp
Text Notes 5050 6350 0    50   ~ 0
The collector-emitter \noperating voltage is \nof this transistor is \nabout 1.6 V.
Text Notes 5350 1300 0    50   ~ 0
Each of these is an infrared LED with a foward operating \nvoltage of 1.33 V @ 60 mA.  Normally, operating LEDs in \nparallel is problematic due to tolerance variations in each \nLED, but with seven LEDs in each string, it is expected that \nsuch variations should average out if the LEDs are \nrandomly selected for each string (i.e. don't use all LEDs \nfrom the same batch in one string).
Text Notes 1250 3100 0    50   ~ 0
When the transistor below is on, the voltage \nacross this current limiting resistor bank \nshould be about 12.2 V - (7 * 1.33 V) - 1.6 V, \nor 1.29 V.  The total parallel resistance of \nthe bank is 4.286 ohms, so the current will \nbe 1.29/4.286, or 0.301 A.  Each string of \nLEDs will thus get 0.0752 A.\nCurrent to the entire LED array may be \nincreased up to a maximum of 0.400 A \nby changing resistor values and/or omitting \nresistors from the PCB.
Text Notes 1600 4100 0    50   ~ 0
Actual supply voltage \nis 12.2 volts.
Text Notes 2950 5550 0    50   ~ 0
The base resistor value is determined from the \nformula Rbase = 0.2 * Rload * hFE.  The current \ngain (hFE) for the transistor is 100, so Rbase \nshould be Rbase = 0.2 * 4.286 * 100 = 85.72 ohms.  \nA standard 100 ohm resistor should suffice.
$Comp
L power:GND #PWR04
U 1 1 600D836D
P 2600 6700
F 0 "#PWR04" H 2600 6450 50  0001 C CNN
F 1 "GND" H 2605 6527 50  0000 C CNN
F 2 "" H 2600 6700 50  0001 C CNN
F 3 "" H 2600 6700 50  0001 C CNN
	1    2600 6700
	1    0    0    -1  
$EndComp
$Comp
L Device:R R1
U 1 1 605832F3
P 3450 3200
F 0 "R1" V 3550 3150 50  0000 L CNN
F 1 "15" V 3450 3150 50  0000 L CNN
F 2 "Resistor_SMD:R_0805_2012Metric_Pad1.15x1.40mm_HandSolder" V 3380 3200 50  0001 C CNN
F 3 "~" H 3450 3200 50  0001 C CNN
	1    3450 3200
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R2
U 1 1 6055A128
P 3450 2700
F 0 "R2" V 3550 2650 50  0000 L CNN
F 1 "15" V 3450 2650 50  0000 L CNN
F 2 "Resistor_SMD:R_0805_2012Metric_Pad1.15x1.40mm_HandSolder" V 3380 2700 50  0001 C CNN
F 3 "~" H 3450 2700 50  0001 C CNN
	1    3450 2700
	0    -1   -1   0   
$EndComp
$Comp
L SamacSys_Parts:MMBT2222ALT3G Q1
U 1 1 60565CF4
P 5000 5750
F 0 "Q1" H 5400 6015 50  0000 C CNN
F 1 "MMBT2222ALT3G" H 5400 5924 50  0000 C CNN
F 2 "Mouser-footprints:SOT96P237X111-3N" H 5650 5850 50  0001 L CNN
F 3 "http://www.onsemi.com/pub/Collateral/MMBT2222LT1-D.PDF" H 5650 5750 50  0001 L CNN
F 4 "" H 5650 5650 50  0001 L CNN "Description"
F 5 "1.11" H 5650 5550 50  0001 L CNN "Height"
F 6 "863-MMBT2222ALT3G" H 5650 5450 50  0001 L CNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/ON-Semiconductor/MMBT2222ALT3G?qs=R2UZ7gjkEjJUeR4kVVA5Qw%3D%3D" H 5650 5350 50  0001 L CNN "Mouser Price/Stock"
F 8 "ON Semiconductor" H 5650 5250 50  0001 L CNN "Manufacturer_Name"
F 9 "MMBT2222ALT3G" H 5650 5150 50  0001 L CNN "Manufacturer_Part_Number"
	1    5000 5750
	1    0    0    -1  
$EndComp
$Comp
L IR-LED-driver-28-rescue:CPU-custom J1
U 1 1 6057FA89
P 2300 5750
F 0 "J1" H 2200 6050 50  0000 C CNN
F 1 "CPU" H 2200 5450 50  0000 C CNN
F 2 "custom-footprints:PinHeader_1x05_P2.54mm_Horiz_SMD" H 2300 5750 50  0001 C CNN
F 3 "" H 2300 5750 50  0001 C CNN
	1    2300 5750
	1    0    0    -1  
$EndComp
Wire Wire Line
	1900 4350 1900 4450
Wire Wire Line
	1900 4450 2300 4450
Wire Wire Line
	2300 4350 2300 4450
Connection ~ 2300 4450
Wire Wire Line
	2300 4450 2600 4450
$Comp
L SamacSys_Parts:TSHG6200 LED4
U 1 1 6058E901
P 5400 3700
F 0 "LED4" V 5746 3570 50  0000 R CNN
F 1 "TSHG6200" V 5655 3570 50  0000 R CNN
F 2 "Mouser-footprints:TSHG6200" H 5900 3850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 5900 3750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 5900 3650 50  0001 L BNN "Description"
F 5 "9" H 5900 3550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 5900 3450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 5900 3350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 5900 3250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 5900 3150 50  0001 L BNN "Manufacturer_Part_Number"
	1    5400 3700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED6
U 1 1 605939B4
P 6100 3700
F 0 "LED6" V 6446 3570 50  0000 R CNN
F 1 "TSHG6200" V 6355 3570 50  0000 R CNN
F 2 "Mouser-footprints:TSHG6200" H 6600 3850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 6600 3750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 6600 3650 50  0001 L BNN "Description"
F 5 "9" H 6600 3550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 6600 3450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 6600 3350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 6600 3250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 6600 3150 50  0001 L BNN "Manufacturer_Part_Number"
	1    6100 3700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED8
U 1 1 60594DCE
P 6800 3700
F 0 "LED8" V 7146 3570 50  0000 R CNN
F 1 "TSHG6200" V 7055 3570 50  0000 R CNN
F 2 "Mouser-footprints:TSHG6200" H 7300 3850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 7300 3750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 7300 3650 50  0001 L BNN "Description"
F 5 "9" H 7300 3550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 7300 3450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 7300 3350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 7300 3250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 7300 3150 50  0001 L BNN "Manufacturer_Part_Number"
	1    6800 3700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED10
U 1 1 60596268
P 7500 3700
F 0 "LED10" V 7846 3570 50  0000 R CNN
F 1 "TSHG6200" V 7755 3570 50  0000 R CNN
F 2 "Mouser-footprints:TSHG6200" H 8000 3850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 8000 3750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 8000 3650 50  0001 L BNN "Description"
F 5 "9" H 8000 3550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 8000 3450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 8000 3350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 8000 3250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 8000 3150 50  0001 L BNN "Manufacturer_Part_Number"
	1    7500 3700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED12
U 1 1 60597635
P 8200 3700
F 0 "LED12" V 8546 3570 50  0000 R CNN
F 1 "TSHG6200" V 8455 3570 50  0000 R CNN
F 2 "Mouser-footprints:TSHG6200" H 8700 3850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 8700 3750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 8700 3650 50  0001 L BNN "Description"
F 5 "9" H 8700 3550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 8700 3450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 8700 3350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 8700 3250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 8700 3150 50  0001 L BNN "Manufacturer_Part_Number"
	1    8200 3700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED2
U 1 1 60597F67
P 4700 3700
F 0 "LED2" V 5046 3570 50  0000 R CNN
F 1 "TSHG6200" V 4955 3570 50  0000 R CNN
F 2 "Mouser-footprints:TSHG6200" H 5200 3850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 5200 3750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 5200 3650 50  0001 L BNN "Description"
F 5 "9" H 5200 3550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 5200 3450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 5200 3350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 5200 3250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 5200 3150 50  0001 L BNN "Manufacturer_Part_Number"
	1    4700 3700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED14
U 1 1 6059962F
P 8900 3700
F 0 "LED14" V 9246 3570 50  0000 R CNN
F 1 "TSHG6200" V 9155 3570 50  0000 R CNN
F 2 "Mouser-footprints:TSHG6200" H 9400 3850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 9400 3750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 9400 3650 50  0001 L BNN "Description"
F 5 "9" H 9400 3550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 9400 3450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 9400 3350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 9400 3250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 9400 3150 50  0001 L BNN "Manufacturer_Part_Number"
	1    8900 3700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED3
U 1 1 605A8AFE
P 5400 2700
F 0 "LED3" V 5746 2570 50  0000 R CNN
F 1 "TSHG6200" V 5655 2570 50  0000 R CNN
F 2 "Mouser-footprints:TSHG6200" H 5900 2850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 5900 2750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 5900 2650 50  0001 L BNN "Description"
F 5 "9" H 5900 2550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 5900 2450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 5900 2350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 5900 2250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 5900 2150 50  0001 L BNN "Manufacturer_Part_Number"
	1    5400 2700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED5
U 1 1 605A8B0A
P 6100 2700
F 0 "LED5" V 6446 2570 50  0000 R CNN
F 1 "TSHG6200" V 6355 2570 50  0000 R CNN
F 2 "Mouser-footprints:TSHG6200" H 6600 2850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 6600 2750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 6600 2650 50  0001 L BNN "Description"
F 5 "9" H 6600 2550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 6600 2450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 6600 2350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 6600 2250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 6600 2150 50  0001 L BNN "Manufacturer_Part_Number"
	1    6100 2700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED7
U 1 1 605A8B16
P 6800 2700
F 0 "LED7" V 7146 2570 50  0000 R CNN
F 1 "TSHG6200" V 7055 2570 50  0000 R CNN
F 2 "Mouser-footprints:TSHG6200" H 7300 2850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 7300 2750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 7300 2650 50  0001 L BNN "Description"
F 5 "9" H 7300 2550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 7300 2450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 7300 2350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 7300 2250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 7300 2150 50  0001 L BNN "Manufacturer_Part_Number"
	1    6800 2700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED9
U 1 1 605A8B22
P 7500 2700
F 0 "LED9" V 7846 2570 50  0000 R CNN
F 1 "TSHG6200" V 7755 2570 50  0000 R CNN
F 2 "Mouser-footprints:TSHG6200" H 8000 2850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 8000 2750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 8000 2650 50  0001 L BNN "Description"
F 5 "9" H 8000 2550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 8000 2450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 8000 2350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 8000 2250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 8000 2150 50  0001 L BNN "Manufacturer_Part_Number"
	1    7500 2700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED11
U 1 1 605A8B2E
P 8200 2700
F 0 "LED11" V 8546 2570 50  0000 R CNN
F 1 "TSHG6200" V 8455 2570 50  0000 R CNN
F 2 "Mouser-footprints:TSHG6200" H 8700 2850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 8700 2750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 8700 2650 50  0001 L BNN "Description"
F 5 "9" H 8700 2550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 8700 2450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 8700 2350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 8700 2250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 8700 2150 50  0001 L BNN "Manufacturer_Part_Number"
	1    8200 2700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED1
U 1 1 605A8B3A
P 4700 2700
F 0 "LED1" V 5046 2570 50  0000 R CNN
F 1 "TSHG6200" V 4955 2570 50  0000 R CNN
F 2 "Mouser-footprints:TSHG6200" H 5200 2850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 5200 2750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 5200 2650 50  0001 L BNN "Description"
F 5 "9" H 5200 2550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 5200 2450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 5200 2350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 5200 2250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 5200 2150 50  0001 L BNN "Manufacturer_Part_Number"
	1    4700 2700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED13
U 1 1 605A8B46
P 8900 2700
F 0 "LED13" V 9246 2570 50  0000 R CNN
F 1 "TSHG6200" V 9155 2570 50  0000 R CNN
F 2 "Mouser-footprints:TSHG6200" H 9400 2850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 9400 2750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 9400 2650 50  0001 L BNN "Description"
F 5 "9" H 9400 2550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 9400 2450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 9400 2350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 9400 2250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 9400 2150 50  0001 L BNN "Manufacturer_Part_Number"
	1    8900 2700
	-1   0    0    1   
$EndComp
Wire Wire Line
	4100 2700 4000 2700
Wire Wire Line
	4000 2700 4000 3200
Wire Wire Line
	4000 3700 4100 3700
Wire Wire Line
	3600 2700 3700 2700
Wire Wire Line
	3700 2700 3700 3200
Wire Wire Line
	3700 3700 3600 3700
Wire Wire Line
	3600 3200 3700 3200
Connection ~ 3700 3200
Wire Wire Line
	3700 3200 3700 3700
Wire Wire Line
	3700 3200 4000 3200
Connection ~ 4000 3200
Wire Wire Line
	4000 3200 4000 3700
Wire Wire Line
	3300 2700 3200 2700
Wire Wire Line
	3200 2700 3200 3200
Wire Wire Line
	3200 3700 3300 3700
Wire Wire Line
	3300 3200 3200 3200
Connection ~ 3200 3200
Wire Wire Line
	3200 3200 3200 3700
Wire Wire Line
	4700 2700 4800 2700
Wire Wire Line
	5400 2700 5500 2700
Wire Wire Line
	6100 2700 6200 2700
Wire Wire Line
	6800 2700 6900 2700
Wire Wire Line
	7500 2700 7600 2700
Wire Wire Line
	8200 2700 8300 2700
Wire Wire Line
	4700 3700 4800 3700
Wire Wire Line
	5400 3700 5500 3700
Wire Wire Line
	6100 3700 6200 3700
Wire Wire Line
	6800 3700 6900 3700
Wire Wire Line
	7500 3700 7600 3700
Wire Wire Line
	8200 3700 8300 3700
Wire Wire Line
	8900 2700 9000 2700
Wire Wire Line
	9000 2700 9000 3200
Wire Wire Line
	9000 3700 8900 3700
Wire Wire Line
	3200 3200 2600 3200
Wire Wire Line
	2600 3200 2600 4450
Connection ~ 2600 4450
Wire Wire Line
	9000 3200 9350 3200
Connection ~ 9000 3200
Wire Wire Line
	9000 3200 9000 3700
Text Notes 650  6050 0    50   ~ 0
PWR and GND pins are duplicated \nto allow power to be passed thru \nto other devices.  A track width of \n1.49 mm between PWR pins and \nGND pins with 1-oz copper will \ncarry up to 1.6 A.
$Comp
L SamacSys_Parts:TSHG6200 LED15
U 1 1 60791A4B
P 4700 1700
F 0 "LED15" H 5000 1433 50  0000 C CNN
F 1 "TSHG6200" H 5000 1524 50  0000 C CNN
F 2 "Mouser-footprints:TSHG6200" H 5200 1850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 5200 1750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 5200 1650 50  0001 L BNN "Description"
F 5 "9" H 5200 1550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 5200 1450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 5200 1350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 5200 1250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 5200 1150 50  0001 L BNN "Manufacturer_Part_Number"
	1    4700 1700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED17
U 1 1 6079B0E1
P 5400 1700
F 0 "LED17" H 5700 1433 50  0000 C CNN
F 1 "TSHG6200" H 5700 1524 50  0000 C CNN
F 2 "Mouser-footprints:TSHG6200" H 5900 1850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 5900 1750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 5900 1650 50  0001 L BNN "Description"
F 5 "9" H 5900 1550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 5900 1450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 5900 1350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 5900 1250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 5900 1150 50  0001 L BNN "Manufacturer_Part_Number"
	1    5400 1700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED19
U 1 1 6079DA39
P 6100 1700
F 0 "LED19" H 6400 1433 50  0000 C CNN
F 1 "TSHG6200" H 6400 1524 50  0000 C CNN
F 2 "Mouser-footprints:TSHG6200" H 6600 1850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 6600 1750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 6600 1650 50  0001 L BNN "Description"
F 5 "9" H 6600 1550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 6600 1450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 6600 1350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 6600 1250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 6600 1150 50  0001 L BNN "Manufacturer_Part_Number"
	1    6100 1700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED21
U 1 1 6079F407
P 6800 1700
F 0 "LED21" H 7100 1433 50  0000 C CNN
F 1 "TSHG6200" H 7100 1524 50  0000 C CNN
F 2 "Mouser-footprints:TSHG6200" H 7300 1850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 7300 1750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 7300 1650 50  0001 L BNN "Description"
F 5 "9" H 7300 1550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 7300 1450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 7300 1350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 7300 1250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 7300 1150 50  0001 L BNN "Manufacturer_Part_Number"
	1    6800 1700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED23
U 1 1 607A03D1
P 7500 1700
F 0 "LED23" H 7800 1433 50  0000 C CNN
F 1 "TSHG6200" H 7800 1524 50  0000 C CNN
F 2 "Mouser-footprints:TSHG6200" H 8000 1850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 8000 1750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 8000 1650 50  0001 L BNN "Description"
F 5 "9" H 8000 1550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 8000 1450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 8000 1350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 8000 1250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 8000 1150 50  0001 L BNN "Manufacturer_Part_Number"
	1    7500 1700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED25
U 1 1 607A16F9
P 8200 1700
F 0 "LED25" H 8500 1433 50  0000 C CNN
F 1 "TSHG6200" H 8500 1524 50  0000 C CNN
F 2 "Mouser-footprints:TSHG6200" H 8700 1850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 8700 1750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 8700 1650 50  0001 L BNN "Description"
F 5 "9" H 8700 1550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 8700 1450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 8700 1350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 8700 1250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 8700 1150 50  0001 L BNN "Manufacturer_Part_Number"
	1    8200 1700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED27
U 1 1 607A2A81
P 8900 1700
F 0 "LED27" H 9200 1433 50  0000 C CNN
F 1 "TSHG6200" H 9200 1524 50  0000 C CNN
F 2 "Mouser-footprints:TSHG6200" H 9400 1850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 9400 1750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 9400 1650 50  0001 L BNN "Description"
F 5 "9" H 9400 1550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 9400 1450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 9400 1350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 9400 1250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 9400 1150 50  0001 L BNN "Manufacturer_Part_Number"
	1    8900 1700
	-1   0    0    1   
$EndComp
Wire Wire Line
	4000 2700 4000 1700
Wire Wire Line
	4000 1700 4100 1700
Connection ~ 4000 2700
Wire Wire Line
	4700 1700 4800 1700
Wire Wire Line
	5400 1700 5500 1700
Wire Wire Line
	6100 1700 6200 1700
Wire Wire Line
	6800 1700 6900 1700
Wire Wire Line
	7500 1700 7600 1700
Wire Wire Line
	8200 1700 8300 1700
Wire Wire Line
	8900 1700 9000 1700
Wire Wire Line
	9000 1700 9000 2700
Connection ~ 9000 2700
Wire Wire Line
	2400 5950 2600 5950
Connection ~ 2600 5950
Wire Wire Line
	2600 5950 2600 6600
Wire Wire Line
	2400 5850 2600 5850
Wire Wire Line
	2600 5850 2600 5950
Wire Wire Line
	5000 5850 2600 5850
Connection ~ 2600 5850
Wire Wire Line
	5000 5750 4000 5750
Wire Wire Line
	3700 5750 2400 5750
Wire Wire Line
	2600 5650 2400 5650
Wire Wire Line
	2600 4450 2600 5550
Wire Wire Line
	2600 5550 2400 5550
Connection ~ 2600 5550
Wire Wire Line
	2600 5550 2600 5650
Wire Wire Line
	2350 6500 2350 6600
Wire Wire Line
	2350 6600 2600 6600
Connection ~ 2600 6600
Wire Wire Line
	2600 6600 2600 6700
Wire Wire Line
	5800 5750 9350 5750
Wire Wire Line
	9350 3200 9350 5750
$Comp
L SamacSys_Parts:TSHG6200 LED16
U 1 1 607C3B18
P 4700 4700
F 0 "LED16" H 5000 4433 50  0000 C CNN
F 1 "TSHG6200" H 5000 4524 50  0000 C CNN
F 2 "Mouser-footprints:TSHG6200" H 5200 4850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 5200 4750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 5200 4650 50  0001 L BNN "Description"
F 5 "9" H 5200 4550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 5200 4450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 5200 4350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 5200 4250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 5200 4150 50  0001 L BNN "Manufacturer_Part_Number"
	1    4700 4700
	-1   0    0    1   
$EndComp
Wire Wire Line
	4000 3700 4000 4700
Wire Wire Line
	4000 4700 4100 4700
Connection ~ 4000 3700
$Comp
L SamacSys_Parts:TSHG6200 LED18
U 1 1 607CAC28
P 5400 4700
F 0 "LED18" H 5700 4433 50  0000 C CNN
F 1 "TSHG6200" H 5700 4524 50  0000 C CNN
F 2 "Mouser-footprints:TSHG6200" H 5900 4850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 5900 4750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 5900 4650 50  0001 L BNN "Description"
F 5 "9" H 5900 4550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 5900 4450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 5900 4350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 5900 4250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 5900 4150 50  0001 L BNN "Manufacturer_Part_Number"
	1    5400 4700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED20
U 1 1 607CC120
P 6100 4700
F 0 "LED20" H 6400 4433 50  0000 C CNN
F 1 "TSHG6200" H 6400 4524 50  0000 C CNN
F 2 "Mouser-footprints:TSHG6200" H 6600 4850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 6600 4750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 6600 4650 50  0001 L BNN "Description"
F 5 "9" H 6600 4550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 6600 4450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 6600 4350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 6600 4250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 6600 4150 50  0001 L BNN "Manufacturer_Part_Number"
	1    6100 4700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED22
U 1 1 607CCDE8
P 6800 4700
F 0 "LED22" H 7100 4433 50  0000 C CNN
F 1 "TSHG6200" H 7100 4524 50  0000 C CNN
F 2 "Mouser-footprints:TSHG6200" H 7300 4850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 7300 4750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 7300 4650 50  0001 L BNN "Description"
F 5 "9" H 7300 4550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 7300 4450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 7300 4350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 7300 4250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 7300 4150 50  0001 L BNN "Manufacturer_Part_Number"
	1    6800 4700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED24
U 1 1 607CDA11
P 7500 4700
F 0 "LED24" H 7800 4433 50  0000 C CNN
F 1 "TSHG6200" H 7800 4524 50  0000 C CNN
F 2 "Mouser-footprints:TSHG6200" H 8000 4850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 8000 4750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 8000 4650 50  0001 L BNN "Description"
F 5 "9" H 8000 4550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 8000 4450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 8000 4350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 8000 4250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 8000 4150 50  0001 L BNN "Manufacturer_Part_Number"
	1    7500 4700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED26
U 1 1 607CF130
P 8200 4700
F 0 "LED26" H 8500 4433 50  0000 C CNN
F 1 "TSHG6200" H 8500 4524 50  0000 C CNN
F 2 "Mouser-footprints:TSHG6200" H 8700 4850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 8700 4750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 8700 4650 50  0001 L BNN "Description"
F 5 "9" H 8700 4550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 8700 4450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 8700 4350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 8700 4250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 8700 4150 50  0001 L BNN "Manufacturer_Part_Number"
	1    8200 4700
	-1   0    0    1   
$EndComp
$Comp
L SamacSys_Parts:TSHG6200 LED28
U 1 1 607D3825
P 8900 4700
F 0 "LED28" H 9200 4433 50  0000 C CNN
F 1 "TSHG6200" H 9200 4524 50  0000 C CNN
F 2 "Mouser-footprints:TSHG6200" H 9400 4850 50  0001 L BNN
F 3 "https://www.arrow.com/en/products/tshg6200/vishay" H 9400 4750 50  0001 L BNN
F 4 "TSHG6200 Vishay, 850nm IR LED, 5mm (T-1 3/4) Through Hole package" H 9400 4650 50  0001 L BNN "Description"
F 5 "9" H 9400 4550 50  0001 L BNN "Height"
F 6 "782-TSHG6200" H 9400 4450 50  0001 L BNN "Mouser Part Number"
F 7 "https://www.mouser.co.uk/ProductDetail/Vishay-Semiconductors/TSHG6200?qs=%2Fjqivxn91ccFm7bONgVn3A%3D%3D" H 9400 4350 50  0001 L BNN "Mouser Price/Stock"
F 8 "Vishay" H 9400 4250 50  0001 L BNN "Manufacturer_Name"
F 9 "TSHG6200" H 9400 4150 50  0001 L BNN "Manufacturer_Part_Number"
	1    8900 4700
	-1   0    0    1   
$EndComp
Wire Wire Line
	9000 3700 9000 4700
Wire Wire Line
	9000 4700 8900 4700
Connection ~ 9000 3700
Wire Wire Line
	8300 4700 8200 4700
Wire Wire Line
	7600 4700 7500 4700
Wire Wire Line
	6900 4700 6800 4700
Wire Wire Line
	6200 4700 6100 4700
Wire Wire Line
	5500 4700 5400 4700
Wire Wire Line
	4800 4700 4700 4700
$EndSCHEMATC
