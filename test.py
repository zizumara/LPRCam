#! /usr/bin/python3
#
# test.py:
# Test interfaces to Pi HQ camera and associated hardware.
#
# Hardware/Firmware
# DC Motor Control w/Encoder v1.1 / PIC project focus-motor-control
# Dual Optical Limit Switch v1.2 / PIC project focus-motor-control
# Light Sensor I2C v1.0 / PIC project light-sensor-I2C
# 28 IR LED Driver v1.0 / KiCAD project IR-LED-driver-28
# Arducam 12.3 MP HQ camera with automatic IR-cut filter (Buster version)
#

import time
import smbus
import subprocess
import RPi.GPIO as GPIO

# GPIO output pins
GPIO_IR_ILLUM   = 11    # 1 = turn on IR LED illuminator
GPIO_PROCESSING = 15    # 1 = green processing status LED on
GPIO_RUNNING    = 16    # 1 = red running status LED on
GPIO_SHUTDOWN   = 26    # 1 = shutdown request
GPIO_IRCUT_ENA  = 31    # 1 = enable H-bridge filter control
GPIO_IRCUT_IN   = 32    # 1 = insert filter to remove IR during daylight
GPIO_IRCUT_MODE = 33    # 1 = use simple H-bridge mode for IR filter control

# ANSI escape sequences for text colors
C_RED = '\033[91m'
C_BLUE = '\033[94m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_MAGENTA = '\033[95m'
C_END = '\033[0m'

# Light meter I2C register offsets
METER_AVG_L       = 0   # time-averaged light reading
METER_AVG_H       = 1
METER_MEAS_L      = 2   # instantaneous light reading
METER_MEAS_H      = 3
METER_RFRSH_SEC_L = 4   # number of seconds to refresh sliding window average
METER_RFRSH_SEC_H = 5
METER_TRIG_L      = 6   # threshold light reading for trigger signal (not used)
METER_TRIG_H      = 7
METER_BUFF_SIZE   = 8

I2C_ADDR_METER = 0x30 # I2C address of light meter
REFRESH_SEC = 600     # seconds to refresh light level sliding average window

# Focus controller I2C register offsets and masks.
FOCUS_CMD         = 0   # command to controller (see CMD_? below)
FOCUS_STS         = 1   # status from controller (currently active command)
FOCUS_POS_REQ_L   = 2   # software requested axle position (LSByte)
FOCUS_POS_REQ_H   = 3   # software requested axle position (MSByte)
FOCUS_POS_MEAS_L  = 4   # measured axle position (LSByte)
FOCUS_POS_MEAS_H  = 5   # measured axle position (MSByte)
FOCUS_POS_MAX_L   = 6   # maximum encoder measured position (LSByte)
FOCUS_POS_MAX_H   = 7   # maximum encoder measured position (MSByte)
FOCUS_SW_STS      = 8   # limit switch status
FOCUS_DEADBAND    = 9   # positioning deadband
FOCUS_SPEED_REQ   = 10  # requested motor speed (0-255)
FOCUS_SPEED_CURR  = 11  # current motor speed
FOCUS_DIR_CURR    = 12  # current motor direction (CW=1, CCW=2)
FOCUS_ENC_LIMIT_L = 13  # encoder travel limit (LSByte)
FOCUS_ENC_LIMIT_H = 14  # encoder travel limit (MSByte)
FOCUS_ENC_FAULT_L = 15  # encoder travel limit fault status (LSByte)
FOCUS_ENC_FAULT_H = 16  # encoder travel limit fault status (MSByte)
FOCUS_NVM_INDEX   = 17  # word index for accessing NVM data
FOCUS_NVM_DATA_L  = 18  # data for NVM testing (LSByte)
FOCUS_NVM_DATA_H  = 19  # data for NVM testing (MSByte)
FOCUS_BUFF_SIZE   = 20  # size of buffer for above registers

CW_CURRENT_MASK  = 0x01  # currently at clockwise limit
CCW_CURRENT_MASK = 0x02  # currently at counterclockwise limit
CW_TRIPPED_MASK  = 0x10  # clockwise limit switch was recently triggered
CCW_TRIPPED_MASK = 0x20  # counterclockwise limit switch was recently triggered

I2C_ADDR_FOCUS = 0x22

FOCUS_CMD_INVALID     = -1
FOCUS_CMD_NONE        = 0
FOCUS_CMD_DISABLE     = 1
FOCUS_CMD_ENABLE      = 2
FOCUS_CMD_RUN_TO_POS  = 3
FOCUS_CMD_RUN_CW      = 4
FOCUS_CMD_RUN_CCW     = 5
FOCUS_CMD_CALIBRATE   = 6
FOCUS_CMD_SET_ENC_LIM = 7
FOCUS_CMD_SET_ENC_FLT = 8
FOCUS_CMD_READ_NVM    = 9
FOCUS_CMD_WRITE_NVM   = 10

cmdDict = { FOCUS_CMD_NONE       : 'no active command',
            FOCUS_CMD_DISABLE    : 'disable motor (no brake)',
            FOCUS_CMD_ENABLE     : 'enable motor at speed 0 (brake)',
            FOCUS_CMD_RUN_TO_POS : 'run to the requested position',
            FOCUS_CMD_RUN_CW     : 'run CW at requested speed',
            FOCUS_CMD_RUN_CCW    : 'run CCW at requested speed',
            FOCUS_CMD_CALIBRATE  : 'calibrate limits',
            FOCUS_CMD_SET_ENC_LIM: 'set encoder limit',
            FOCUS_CMD_SET_ENC_FLT: 'set encoder fault',
            FOCUS_CMD_READ_NVM   : 'read NVM data',
            FOCUS_CMD_WRITE_NVM  : 'write NVM data' }

stsDict = { FOCUS_CMD_NONE       : 'no active command    ',
            FOCUS_CMD_DISABLE    : 'motor disabled       ',
            FOCUS_CMD_ENABLE     : 'motor enabled w/brake',
            FOCUS_CMD_RUN_TO_POS : 'running to position  ',
            FOCUS_CMD_RUN_CW     : 'running CW to limit  ',
            FOCUS_CMD_RUN_CCW    : 'running CCW to limit ',
            FOCUS_CMD_CALIBRATE  : 'calibrating limits   ',
            FOCUS_CMD_SET_ENC_LIM: 'setting encoder limit',
            FOCUS_CMD_SET_ENC_FLT: 'setting encoder fault',
            FOCUS_CMD_READ_NVM   : 'reading NVM data     ',
            FOCUS_CMD_WRITE_NVM  : 'writing NVM data     ' }

# Focus motor encoder fault status.
FOCUS_ENC_OK        = 1
FOCUS_ENC_CW_FAULT  = 2
FOCUS_ENC_CCW_FAULT = 3

# User menu structure

MENUSEL_INVALID      = -1
MENUSEL_DISABLE      = 0
MENUSEL_RUN_TO_POS   = 1
MENUSEL_SET_DBAND    = 2
MENUSEL_REPEAT_STS   = 3
MENUSEL_TOGGLE_IRLED = 4
MENUSEL_TOGGLE_IRCUT = 5
MENUSEL_TOGGLE_LEDS  = 6
MENUSEL_CALIBRATE    = 7
MENUSEL_SET_ENC_LIM  = 8
MENUSEL_SET_ENC_FLT  = 9
MENUSEL_READ_NVM     = 10
MENUSEL_WRITE_NVM    = 11
MENUSEL_PHOTO_PARMS  = 12
MENUSEL_TAKE_PHOTO   = 13

menuDict = { MENUSEL_DISABLE      : 'Disable motor (no brake)',
             MENUSEL_RUN_TO_POS   : 'Run to specified position',
             MENUSEL_SET_DBAND    : 'Set positioning deadband',
             MENUSEL_REPEAT_STS   : 'Read status continuously',
             MENUSEL_TOGGLE_IRLED : 'Toggle IR LEDs on/off',
             MENUSEL_TOGGLE_IRCUT : 'Toggle IR cut filter in/out',
             MENUSEL_TOGGLE_LEDS  : 'Toggle status LEDs',
             MENUSEL_CALIBRATE    : 'Calibrate limits',
             MENUSEL_SET_ENC_LIM  : 'Set encoder travel limit',
             MENUSEL_SET_ENC_FLT  : 'Set encoder fault status',
             MENUSEL_READ_NVM     : 'Read from specific NVM location',
             MENUSEL_WRITE_NVM    : 'Write to specific NVM location',
             MENUSEL_PHOTO_PARMS  : 'Set photo parameters',
             MENUSEL_TAKE_PHOTO   : 'Take photo' }


# Function definitions

def sendFocusCommand(bus, register, data, numBytes=1):
    isSuccess = False
    try:
        if numBytes == 1:
            bus.write_byte_data(I2C_ADDR_FOCUS, register, data)
            print(f'0x{data:02x} written to controller at register {register}.')
        elif numBytes == 2:
            lsb = data & 0x00ff
            msb = (data >> 8) & 0x00ff
            bus.write_byte_data(I2C_ADDR_FOCUS, register, lsb)
            bus.write_byte_data(I2C_ADDR_FOCUS, register+1, msb)
            print(f'0x{data:04x} written to controller at register {register}.')
        isSuccess = True
    except:
        print(f'Unable to write to controller at I2C address 0x{I2C_ADDR_FOCUS:02x}.')
    return isSuccess

def getFocusStatus(bus, buff):
    isSuccess = True
    for i in range(FOCUS_BUFF_SIZE):
        try:
            buff[i] = bus.read_byte_data(I2C_ADDR_FOCUS, i)
        except:
            print(f'Unable to read from controller at I2C address 0x{I2C_ADDR_FOCUS:02x}.')
            isSuccess = False
            break
    return isSuccess

def encStsToString(encoderSts):
    if encoderSts == FOCUS_ENC_OK:
       stsStr = f'{C_GREEN}OK{C_END}'
    elif encoderSts == FOCUS_ENC_CW_FAULT:
       stsStr = f'{C_RED}CW FAULT{C_END}'
    elif encoderSts == FOCUS_ENC_CCW_FAULT:
       stsStr = f'{C_RED}CCW FAULT{C_END}'
    else:
       stsStr = f'{C_YELLOW}0x{encoderSts:02x}{C_END}'
    return stsStr

def swStsToString(switchSts):
    cwCurr = True if switchSts & CW_CURRENT_MASK else False
    ccwCurr = True if switchSts & CCW_CURRENT_MASK else False
    cwTrip = True if switchSts & CW_TRIPPED_MASK else False
    ccwTrip = True if switchSts & CCW_TRIPPED_MASK else False
    if cwTrip:
        stsStr = f'trig {C_YELLOW} CW{C_END}'
    else:
        stsStr = f'trig ___'
    if ccwTrip:
        stsStr += f':{C_YELLOW}CCW{C_END}'
    else:
        stsStr += f':___'
    if cwCurr and not ccwCurr:
        stsStr += f', {C_YELLOW}CW limit {C_END}'
    elif ccwCurr and not cwCurr:
        stsStr += f', {C_YELLOW}CCW limit{C_END}'
    elif not cwCurr and not ccwCurr:
        stsStr += f'           '
    else:
        stsStr += f', {C_RED}limit err{C_END}'
    return stsStr

def initLightMeter(bus):
    """
    Given the I2C interface to the light meter, initialize the light meter by setting
    the sliding window average refresh interval and take the first reading.
    Returns:
        i2cOK - True only if I2C interface is working
        levelNow - current darkness level
        levelAvg - average darkness level over refresh interval
    """
    i2cOK = False
    i2cBuff = [0] * METER_BUFF_SIZE
    levelNow = 0
    levelAvg = 0
    rfrshSecLow = int(REFRESH_SEC & 0xff)
    rfrshSecHigh = int(REFRESH_SEC / 256)
    try:
        bus.write_byte_data(I2C_ADDR_METER, METER_RFRSH_SEC_L, rfrshSecLow)
        bus.write_byte_data(I2C_ADDR_METER, METER_RFRSH_SEC_H, rfrshSecHigh)
        time.sleep(0.2)
        for i in range(METER_BUFF_SIZE):
            i2cBuff[i] = bus.read_byte_data(I2C_ADDR_METER, i)
        levelNow = (i2cBuff[METER_MEAS_H] * 256) + i2cBuff[METER_MEAS_L]
        levelAvg = (i2cBuff[METER_AVG_H] * 256)  + i2cBuff[METER_AVG_L]
        i2cOK = True
    except:
        logging.info(f'ERROR: initLightMeter() unable to access I2C '
                     f'interface at address 0x{I2C_ADDR_METER:02x}')

    return i2cOK, levelNow, levelAvg

def getLightLevel(bus):
    """
    Given the I2C interface to the light meter, take a reading.
    Returns:
        i2cOK - True only if I2C interface is working
        levelNow - current darkness level
        levelAvg - average darkness level over refresh interval
    """
    i2cOK = False
    i2cBuff = [0] * METER_BUFF_SIZE
    levelNow = 0
    levelAvg = 0
    try:
        for i in range(METER_BUFF_SIZE):
            i2cBuff[i] = bus.read_byte_data(I2C_ADDR_METER, i)
        levelNow = (i2cBuff[METER_MEAS_H] * 256) + i2cBuff[METER_MEAS_L]
        levelAvg = (i2cBuff[METER_AVG_H] * 256)  + i2cBuff[METER_AVG_L]
        i2cOK = True
    except:
        logging.info(f'ERROR: getLightLevel() unable to access I2C '
                     f'interface at address 0x{I2C_ADDR_METER:02x}')

    return i2cOK, levelNow, levelAvg


########################################################################################
# MAIN PROGRAM

# Initialize GPIOs.
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(GPIO_PROCESSING, GPIO.OUT)
GPIO.setup(GPIO_RUNNING, GPIO.OUT)
GPIO.output(GPIO_PROCESSING, 0)
GPIO.output(GPIO_RUNNING, 0)
areLEDs_on = False
GPIO.setup(GPIO_IR_ILLUM, GPIO.OUT)
GPIO.output(GPIO_IR_ILLUM, 0)
isIRLED_on = False
GPIO.setup(GPIO_IRCUT_MODE, GPIO.OUT)
GPIO.setup(GPIO_IRCUT_ENA, GPIO.OUT)
GPIO.setup(GPIO_IRCUT_IN, GPIO.OUT)
GPIO.output(GPIO_IRCUT_MODE, 1)
GPIO.output(GPIO_IRCUT_IN, 1)
GPIO.output(GPIO_IRCUT_ENA, 1)
time.sleep(0.5)
GPIO.output(GPIO_IRCUT_ENA, 0)
isIRCUT_in = True
GPIO.setup(GPIO_SHUTDOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
isShutdownDisarmed = GPIO.input(GPIO_SHUTDOWN)

# Create an object to access the I2C interface (1 = /dev/i2c-1).
i2c = smbus.SMBus(1)

isMeterOK, lightNow, lightAvg = initLightMeter(i2c)
isCalibrated = False
isFocusOK = False
areLEDs_on = False
mode = 'sports'
shutterMs = 1600
digitalGain = 2
analogGain = 12
menuSelect = FOCUS_CMD_INVALID
while True:
    print( '\n' )
    time.sleep(0.5)

    # On each main menu loop, read status from the controller and display it.
    focusBuff = [0] * FOCUS_BUFF_SIZE
    isFocusOK = getFocusStatus(i2c, focusBuff)
    focusOKStr = f'{C_GREEN}YES{C_END}' if isFocusOK else f'{C_RED}NO{C_END}'
    calStr = f'{C_GREEN}YES{C_END}' if isCalibrated else f'{C_RED}NO{C_END}'
    time.sleep(0.1)
    print('Focus motor')
    print(f'  connected = {focusOKStr}, calibrated = {calStr}')
    try:
        print(f'  command status = {stsDict[focusBuff[FOCUS_STS]]}')
    except:
        print(f'  command status = 0x{focusBuff[FOCUS_STS]:02x}')
    try:
        print(f'  active command = {cmdDict[focusBuff[FOCUS_CMD]]}')
    except:
        print(f'  active command = 0x{focusBuff[FOCUS_CMD]:02x}')
    encStsStr = encStsToString(focusBuff[FOCUS_ENC_FAULT_L])
    encLimit = focusBuff[FOCUS_ENC_LIMIT_L] + focusBuff[FOCUS_ENC_LIMIT_H] * 256
    print(f'  deadband = {focusBuff[FOCUS_DEADBAND]},'
          f' encoder limit = {encLimit},'
          f' encoder fault = {encStsStr}')
    nvmData = focusBuff[FOCUS_NVM_DATA_L] + focusBuff[FOCUS_NVM_DATA_H] * 256
    nvmIndex = focusBuff[FOCUS_NVM_INDEX]
    print(f'  NVM index = {nvmIndex}, NVM data = {nvmData} (0x{nvmData:04x})')
    print(f'  motor speed: requested = {focusBuff[FOCUS_SPEED_REQ]},'
          f' current = {focusBuff[FOCUS_SPEED_CURR]}')
    if isCalibrated:
        posReqSts = focusBuff[FOCUS_POS_REQ_L] + focusBuff[FOCUS_POS_REQ_H] * 256
        posMeasSts = focusBuff[FOCUS_POS_MEAS_L] + focusBuff[FOCUS_POS_MEAS_H] * 256
        posMaxSts = focusBuff[FOCUS_POS_MAX_L] + focusBuff[FOCUS_POS_MAX_H] * 256
    else:
        posReqSts = f'{C_YELLOW}NA{C_END}'
        posMeasSts = f'{C_YELLOW}NA{C_END}'
        posMaxSts = f'{C_YELLOW}NA{C_END}'
    print(f'  position: requested = {posReqSts}, measured = {posMeasSts}, max = {posMaxSts},'
          f' {swStsToString(focusBuff[FOCUS_SW_STS])}')

    isMeterOK, lightNow, lightAvg = getLightLevel(i2c)
    meterOKStr = f'{C_GREEN}YES{C_END}' if isMeterOK else f'{C_RED}NO{C_END}'
    print(f'Light meter')
    print(f'  connected = {meterOKStr}, level now = {lightNow}, average level = {lightAvg}')

    IRLED_str = 'ON' if isIRLED_on else 'OFF'
    IRCUT_str = 'IN (day)' if isIRCUT_in else 'OUT (night)'
    print(f'Infrared')
    print(f'  IR LED {IRLED_str}, IR cut filter {IRCUT_str}')

    LEDS_str = 'ON' if areLEDs_on else 'OFF'
    isShutdownDisarmed = GPIO.input(GPIO_SHUTDOWN)
    shdnStr = f'DISARMED' if isShutdownDisarmed else '{C_RED}ARMED{C_END}'
    print(f'Shutdown {shdnStr}, LED indicators {LEDS_str}')

    print(f'Photo Parameters:')
    print(f'  mode={mode}, ss={shutterMs}, ag={analogGain}, dg={digitalGain}')

    # Display main menu selections and prompt for choice.
    print( '\nMain Menu')
    for (selectNum, label) in menuDict.items():
        print(f'{selectNum} - {label}')
    print('Q - Quit program')

    menuInput = input('Enter selection:')
    if menuInput == 'Q' or menuInput == 'q':
        print('Quitting...')
        break
    if not menuInput:
        continue
    try:
        menuSelect = int(menuInput)
    except:
        menuSelect = MENUSEL_INVALID
        print(f'{menuInput} is an invalid selection.')

    if menuSelect == MENUSEL_DISABLE:
        sendFocusCommand(i2c, FOCUS_CMD, FOCUS_CMD_DISABLE)

    elif menuSelect == MENUSEL_RUN_TO_POS:
        while True:
            print('\n')
            if not isCalibrated:
                print('Menu item unavailable.  Positioning is uncalibrated.')
                break
            menuInput = input(f'Enter desired position (0-{posMaxSts}) or Q to exit menu:')
            if menuInput == 'Q' or menuInput == 'q':
                break

            try:
                reqPosition = int(menuInput)
            except:
                print(f'{menuInput} is an invalid input.')
            else:
                if reqPosition < 0 or reqPosition > posMaxSts:
                    print(f'{reqPosition} is not in the valid range 0-{posMaxSts}.')
                else:
                    sendFocusCommand(i2c, FOCUS_POS_REQ_L, reqPosition, numBytes=2)
                    time.sleep(0.1)
                    sendFocusCommand(i2c, FOCUS_CMD, FOCUS_CMD_RUN_TO_POS)

    elif menuSelect == MENUSEL_SET_DBAND:
        while True:
            print('\n')
            menuInput = input('Enter deadband parameter (0-255) or Q to exit menu:' )
            if menuInput == 'Q' or menuInput == 'q':
                break
            try:
                pidParam = int(menuInput)
            except:
                print(f'{menuInput} is an invalid input.')
            else:
                if pidParam < 0 or pidParam > 255:
                    print(f'{pidParam} is not in the valid range 0-255.')
                else:
                    sendFocusCommand(i2c, FOCUS_DEADBAND, pidParam)
                    break

    elif menuSelect == MENUSEL_REPEAT_STS:
        print('\nUse CTL-C to exit')
        while True:
            try:
                getFocusStatus(i2c, focusBuff)
                time.sleep(0.1)
                isMeterOK, lightNow, lightAvg = getLightLevel(i2c)
                if focusBuff[FOCUS_DIR_CURR] == 1:
                    direct = ' CW'
                else:
                    direct = 'CCW'
                posReqSts = focusBuff[FOCUS_POS_REQ_L] + focusBuff[FOCUS_POS_REQ_H] * 256
                posMeasSts = focusBuff[FOCUS_POS_MEAS_L] + focusBuff[FOCUS_POS_MEAS_H] * 256
                isShutdownDisarmed = GPIO.input(GPIO_SHUTDOWN)
                print(f'{time.strftime("%H:%M:%S")} '
                      f'light={lightNow}, '
                      f'sts={focusBuff[FOCUS_STS]:>3d}, '
                      f'rpos={posReqSts:>5d}, '
                      f'mpos={posMeasSts:>5d}, '
                      f'sp={focusBuff[FOCUS_SPEED_CURR]:>3d}, '
                      f'dir={direct}, '
                      f'shdn={isShutdownDisarmed}, '
                      f'{swStsToString(focusBuff[FOCUS_SW_STS])}')
                time.sleep(1.0)
            except SystemExit:
                break
            except KeyboardInterrupt:
                break
        print('\n')

    elif menuSelect == MENUSEL_CALIBRATE:
        sendFocusCommand(i2c, FOCUS_CMD, FOCUS_CMD_ENABLE)
        time.sleep(0.1)
        sendFocusCommand(i2c, FOCUS_CMD, FOCUS_CMD_CALIBRATE)
        startTime = time.time()
        stsCount = 0
        while True:
            try:
                getFocusStatus(i2c, focusBuff)
                status = focusBuff[FOCUS_STS]
                if status == FOCUS_CMD_NONE:
                    isCalibrated = True
                    elapsed = time.time() - startTime
                    print(f'calibration complete - elapsed time {elapsed:.1f} seconds')
                    break
                if stsCount % 10 == 0:
                    stsCount = 0
                    if status in stsDict:
                        print(f'{stsDict[status]}, {swStsToString(focusBuff[FOCUS_SW_STS])} ...')
                    else:
                        print(f'unknown active command 0x{status:02x}...')
                stsCount += 1
                time.sleep(0.2)
            except KeyboardInterrupt:
                sendFocusCommand(i2c, FOCUS_CMD, FOCUS_CMD_DISABLE)
                elapsed = time.time() - startTime
                print(f'Canceled calibration after {elapsed:.1f} seconds')
                break

    elif menuSelect == MENUSEL_TOGGLE_IRLED:
        if isIRLED_on:
            GPIO.output(GPIO_IR_ILLUM, 0)
            isIRLED_on = False
            print('IR illumination is now OFF.')
        else:
            GPIO.output(GPIO_IR_ILLUM, 1)
            isIRLED_on = True
            print('IR illumination is now ON.')

    elif menuSelect == MENUSEL_TOGGLE_IRCUT:
        if isIRCUT_in:
            GPIO.output(GPIO_IRCUT_IN, 0)
            GPIO.output(GPIO_IRCUT_ENA, 1)
            time.sleep(0.5)
            GPIO.output(GPIO_IRCUT_ENA, 0)
            isIRCUT_in = False
            print('IR cut filter is now OUT (nighttime).')
        else:
            GPIO.output(GPIO_IRCUT_IN, 1)
            GPIO.output(GPIO_IRCUT_ENA, 1)
            time.sleep(0.5)
            GPIO.output(GPIO_IRCUT_ENA, 0)
            isIRCUT_in = True
            print('IR cut filter is now IN (daytime).')

    elif menuSelect == MENUSEL_TOGGLE_LEDS:
        if areLEDs_on:
            GPIO.output(GPIO_PROCESSING, 0)
            GPIO.output(GPIO_RUNNING, 0)
            areLEDs_on = False
        else:
            GPIO.output(GPIO_PROCESSING, 1)
            GPIO.output(GPIO_RUNNING, 1)
            areLEDs_on = True

    elif menuSelect == MENUSEL_SET_ENC_LIM:
        while True:
            print('\n')
            menuInput = input('Enter encoder travel limit (0-65535) or Q to exit menu:' )
            if menuInput == 'Q' or menuInput == 'q':
                break
            try:
                encLimit = int(menuInput)
            except:
                print(f'{menuInput} is an invalid input.')
            else:
                if encLimit < 0 or encLimit > 65535:
                    print(f'{encLimit} is not in the valid range 0-65535.')
                else:
                    sendFocusCommand(i2c, FOCUS_ENC_LIMIT_L, encLimit, numBytes=2)
                    time.sleep(0.1)
                    sendFocusCommand(i2c, FOCUS_CMD, FOCUS_CMD_SET_ENC_LIM)
                    time.sleep(1)   # ensure time to write to flash
                    break

    elif menuSelect == MENUSEL_SET_ENC_FLT:
        while True:
            print('\n')
            menuInput = input('Select encoder fault (1=OK, 2=CW fault, 3=CCW fault) or Q to exit menu:' )
            if menuInput == 'Q' or menuInput == 'q':
                break
            try:
                encFault = int(menuInput)
            except:
                print(f'{menuInput} is an invalid input.')
            else:
                if encFault < 1 or encFault > 3:
                    print(f'{encFault} is not in the valid range 1-3.')
                else:
                    sendFocusCommand(i2c, FOCUS_ENC_FAULT_L, encFault)
                    time.sleep(0.1)
                    sendFocusCommand(i2c, FOCUS_CMD, FOCUS_CMD_SET_ENC_FLT)
                    time.sleep(1)   # ensure time to write to flash
                    break

    elif menuSelect == MENUSEL_READ_NVM:
        while True:
            print('\n')
            menuInput = input('Enter NVM word to read (0-31) or Q to exit menu:' )
            if menuInput == 'Q' or menuInput == 'q':
                break
            try:
                nvmIndex = int(menuInput)
            except:
                print(f'{menuInput} is an invalid input.')
            else:
                if nvmIndex < 0 or nvmIndex > 31:
                    print(f'{nvmIndex} is not in the valid range 0-31.')
                else:
                    sendFocusCommand(i2c, FOCUS_NVM_INDEX, nvmIndex)
                    time.sleep(0.1)
                    sendFocusCommand(i2c, FOCUS_CMD, FOCUS_CMD_READ_NVM)
                    time.sleep(1)   # ensure time to read from flash
                    break

    elif menuSelect == MENUSEL_WRITE_NVM:
        while True:
            print('\n')
            menuInput = input('Enter NVM location to write (0-31) or Q to exit menu:' )
            if menuInput == 'Q' or menuInput == 'q':
                break
            try:
                nvmIndex = int(menuInput)
            except:
                print(f'{menuInput} is an invalid input.')
            else:
                if nvmIndex < 0 or nvmIndex > 31:
                    print(f'{nvmIndex} is not in the valid range 0-31.')
                else:
                    menuInput = input('Enter NVM data to write (0-65535) or Q to exit menu:' )
                    if menuInput == 'Q' or menuInput == 'q':
                        break
                    try:
                        nvmData = int(menuInput)
                    except:
                        print(f'{menuInput} is an invalid input.')
                    else:
                        if nvmData < 0 or nvmData > 65535:
                            print(f'{nvmData} is not in the valid range 0-65535.')
                        else:
                            sendFocusCommand(i2c, FOCUS_NVM_INDEX, nvmIndex)
                            time.sleep(0.1)
                            sendFocusCommand(i2c, FOCUS_NVM_DATA_L, nvmData, numBytes=2)
                            time.sleep(0.1)
                            sendFocusCommand(i2c, FOCUS_CMD, FOCUS_CMD_WRITE_NVM)
                            time.sleep(1)   # ensure time to write to flash
                            break

    elif menuSelect == MENUSEL_PHOTO_PARMS:
        while True:
            print('\n')
            menuInput = input('Enter shutter speed in milliseconds or Q to exit menu:' )
            if menuInput == 'Q' or menuInput == 'q':
                break
            try:
                shutterMs = int(menuInput)
            except:
                print(f'{menuInput} is an invalid input.')
            else:
                break
        while True and menuInput != 'Q' and menuInput != 'q':
            print('\n')
            menuInput = input('Enter analog gain (1-12) or Q to exit menu:' )
            if menuInput == 'Q' or menuInput == 'q':
                break
            try:
                analogGain = int(menuInput)
            except:
                print(f'{menuInput} is an invalid input.')
            else:
                if analogGain < 1 or analogGain > 12:
                    print(f'{analogGain} is not in the valid range 1-12.')
                else:
                    break
        while True and menuInput != 'Q' and menuInput != 'q':
            print('\n')
            menuInput = input('Enter digital gain (1-4) or Q to exit menu:' )
            if menuInput == 'Q' or menuInput == 'q':
                break
            try:
                digitalGain = int(menuInput)
            except:
                print(f'{menuInput} is an invalid input.')
            else:
                if digitalGain < 1 or digitalGain > 12:
                    print(f'{digitalGain} is not in the valid range 1-4.')
                else:
                    break
        while True and menuInput != 'Q' and menuInput != 'q':
            print('\n')
            menuInput = input('Select mode (1=sports, 2=night) or Q to exit menu:' )
            if menuInput == 'Q' or menuInput == 'q':
                break
            try:
                modeNum = int(menuInput)
            except:
                print(f'{menuInput} is an invalid input.')
            else:
                if modeNum != 1 and modeNum != 2:
                    print(f'{modeNum} is not in the valid range 1-2.')
                else:
                    if modeNum == 1:
                        mode = 'sports'
                    else:
                        mode = 'night'
                    break

    elif menuSelect == MENUSEL_TAKE_PHOTO:
        file = f'test-ss{shutterMs}ag{analogGain}dg{digitalGain}f{posReqSts:04d}{mode}.jpg'
        cmd = ['raspistill', '-ex', f'{mode}', '-ss', f'{shutterMs}', '-ag', f'{analogGain}',
               '-dg', f'{digitalGain}', '-awb', 'greyworld', '-o', f'{file}']
        photoProc = subprocess.Popen(cmd)
        returnCode = photoProc.poll()
        print(f'Photo output to file {file}.  Return code = {returnCode}.')

    else:
        print(f'{menuInput} is an invalid selection.')
# end of while True main loop

print('\n')
