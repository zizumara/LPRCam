#!/usr/bin/python3
# LPRcam.py

"""
This program operates a street security camera and captures images using
the Motion application.  It also reads the current light level from a
custom light sensor, switches a custom IR illuminator on/off, and controls
an IR-cut filter on the camera.
"""

import sys, subprocess, logging, time, json, re, Sun, datetime
import RPi.GPIO as GPIO
import smbus
from os import path, _exit, listdir, scandir
from pathlib import Path
from datetime import timedelta

MAX_PCT_DISK_USED  = 90    # if % disk used greater than this, exit program

PIN_RUNNING    = 16   # GPIO output pin connected to LED showing running status
PIN_PROCESSING = 15   # GPIO output pin connected to LED showing processing status
PIN_IR_LED_ON  = 11   # GPIO output pin connected to IR LED array transistor
PIN_IR_CUT_OFF = 33   # GPIO output pin connected to camera IR-cut filter

# I2C buffer offsets for interface to light meter.
I2C_AVG_L       = 0   # time-averaged light reading
I2C_AVG_H       = 1
I2C_MEAS_L      = 2   # instantaneous light reading
I2C_MEAS_H      = 3
I2C_RFRSH_SEC_L = 4   # number of seconds to refresh sliding window average
I2C_RFRSH_SEC_H = 5
I2C_TRIG_L      = 6   # threshold light reading for trigger signal (not used)
I2C_TRIG_H      = 7

I2C_BUFF_SIZE   = 8
I2C_ADDR = 0x30       # I2C address of light meter
REFRESH_SEC = 600     # seconds to refresh light level sliding average window

installDir             = '/home/pi/projects/LPRCam/'
motionImageDir         = '/motion'
dayMotionCfgFilePath   = '/home/pi/projects/LPRCam/motion_day.conf'
twilightMotionCfgFilePath  = '/home/pi/projects/LPRCam/motion_twilight.conf'
nightMotionCfgFilePath = '/home/pi/projects/LPRCam/motion_night.conf'
coords = {'longitude' : -77.04, 'latitude' : 38.91 }

timeNextReport   = time.time()
startTime        = time.time()

def timestamp():
    return time.strftime('%Y-%b-%d %H:%M:%S')

def isTimeForStatus(reportPeriodSecs):
    """
    Checks current time and determines whether it is at or past time to create a
    status report.
    """
    global timeNextReport
    isItTime = False
    timeNow = time.time()
    if timeNow >= timeNextReport:
        isItTime = True
        timeNextReport = timeNow + reportPeriodSecs
    return isItTime

def getCPUTemp():
    """
    Returns the processor temperature in Celcius degrees as a string and as a
    floating point value (2-tuple).  If unable to get the temperature, return
    ('unknown', 0.0).  If unable to parse the result as a floating point value,
    return the string from the system with '(bad)' appended to the string.
    """
    cmd = ['/opt/vc/bin/vcgencmd', 'measure_temp']
    proc = subprocess.run(cmd, capture_output=True, text=True)
    match = re.search("temp=(.*)'C", proc.stdout)
    tempCPU = 0.0
    tempCPUStr = 'unknown'
    if match != None:
        tempCPUStr = match.group(1)
        try:
            tempCPU = float(tempCPUStr)
        except:
            tempCPUStr = tempCPUStr + '(bad)'

    return (tempCPUStr, tempCPU)

def getDiskPctUsed():
    """
    Returns percent of storage space used on the SD card.
    """
    cmd = ['df', '-h', '/']
    proc = subprocess.run(cmd, capture_output=True, text=True)
    match = re.search(".+\n\S+\s+\S+\s+\S+\s+\S+\s+(\S+)%", proc.stdout)
    pctUsed = 0
    if match != None:
        pctUsedStr = match.group(1)
        try:
            pctUsed = int(pctUsedStr)
        except:
            logging.info(f'{timestamp()} getDiskPctUsed() - Cannot convert "{pctUsedStr}" to int.')
            pctUsed = 0
    else:
        logging.info(f'{timestamp()} getDiskPctUsed() - Cannot find % disk used in df output:')
        logging.info(pctUsedStr)

    return pctUsed

def stageMotionImages(motionDir, processDir, diagDir, dayTwilightNight, lightLevel):
    """
    Check the Motion output directory for new images.  Move all of the image files
    found to the image processing directory, adding a suffix to the file name which
    indicates whether it is currently day, twilight, or night and the current
    light level.
    Returns: imagesMoved - number of motion images moved to processing
    """
    imgSuffix = f'{dayTwilightNight[0]}{lightLevel:03d}'
    pathIter = Path(motionDir)
    motionImagePaths = [str(file) for file in pathIter.glob('*.jpg') if not str(file).endswith('m.jpg')]
    imagesMoved = 0
    for motionImagePath in motionImagePaths:
        procFileName = path.basename(motionImagePath).replace('.jpg', f'-{imgSuffix}.jpg')
        procFilePath = path.join(processDir, procFileName)
        proc = subprocess.run(['mv', motionImagePath, procFilePath])
        motionDiagPath = motionImagePath.replace('.jpg', 'm.jpg')
        imagesMoved += 1
        if path.exists(motionDiagPath):
            diagFileName = path.basename(motionDiagPath).replace('.jpg', f'-{imgSuffix}.jpg')
            diagFilePath = path.join(diagDir, diagFileName)
            proc = subprocess.run(['mv', motionDiagPath, diagFilePath])
    if imagesMoved > 0:
        print(f'{timestamp()} {imagesMoved} motion image files moved to processing directory.')

    return imagesMoved

def getOldestImage(imageDir):
    """
    For the given motion image directory, find and return the oldest image file, its matching
    diagnostic image (if any), and the number of image files in the directory (excluding
    diagnostic images).
    """
    oldestCaptureImage = None
    oldestDiagImage = None
    pathIter = Path(imageDir)
    imageFiles = [str(file) for file in pathIter.glob('*.jpg') if not str(file).endswith('m.jpg')]
    imagesByAge = sorted(imageFiles)
    imageCount = len(imagesByAge)
    if imageCount > 0:
        oldestCaptureImage = imagesByAge[0]
        diagFile = oldestCaptureImage.replace('.jpg', 'm.jpg')
        if path.exists(diagFile):
            oldestDiagImage = diagFile

    return (oldestCaptureImage, oldestDiagImage, imageCount)

def purgeOldFiles(directory, maxAgeDays):
    """
    Purge the oldest files from the given directory if there are any older than the
    number of days specified.  After the purge, return a 2-tuple of the age in days 
    of the oldest file and the number of files remaining.
    """

    # Scan the directory in age order and check the age of each file against
    # the maximum age in days.  If the file is older than maxAgeDays, remove it.
    # Continue until the first file is found that does not exceed the age limit.
    totalFilesRemoved = 0
    oldestFileAgeDays = 0
    dirEntryList = scandir(directory)     # list of DirEntry objects
    dirEntryFiles = [x for x in dirEntryList if x.is_dir() == False]
    dirEntriesByAge = sorted(dirEntryFiles, key=lambda fileInfo: fileInfo.stat().st_mtime)

    if len(dirEntriesByAge) > 0:
        timeNow = time.time()
        filesRemoved = 0
        for removeFileInfo in dirEntriesByAge:
            fileAgeDays = (timeNow - removeFileInfo.stat().st_mtime) / 86400
            if removeFileInfo.path.endswith('.jpg'):   # only remove jpg files
                if fileAgeDays > maxAgeDays:
                    proc = subprocess.run(['rm', '-f', removeFileInfo.path])
                    if proc.returncode == 0:
                        filesRemoved += 1
                    else:
                        logging.info(f'{timestamp()} WARNING: Unable to remove file'
                                     f' \'{removeFileInfo.path}\'.')
                else:
                    oldestFileAgeDays = fileAgeDays
                    break
        totalFilesRemoved += filesRemoved
        if filesRemoved > 0:
            logging.info(f'{timestamp()} File age limit of {maxAgeDays} days exceeded'
                         f' in {directory}.')
            logging.info(f'{timestamp()} Successfully purged {filesRemoved} old files'
                         f' from {directory}.')

    numFilesRemaining = len(dirEntriesByAge) - totalFilesRemoved

    return (oldestFileAgeDays, numFilesRemaining)

def initLightMeter(i2c):
    """
    Given the I2C interface to the light meter, initialize the light meter by setting
    the sliding window average refresh interval and take the first reading.
    Returns:
        i2cOK - True only if I2C interface is working
        levelNow - current darkness level
        levelAvg - average darkness level over refresh interval
    """
    i2cOK = False
    i2cBuff = [0] * I2C_BUFF_SIZE
    levelNow = 0
    levelAvg = 0
    rfrshSecLow = int(REFRESH_SEC & 0xff)
    rfrshSecHigh = int(REFRESH_SEC / 256)
    try:
        i2c.write_byte_data(I2C_ADDR, I2C_RFRSH_SEC_L, rfrshSecLow)
        i2c.write_byte_data(I2C_ADDR, I2C_RFRSH_SEC_H, rfrshSecHigh)
        time.sleep(0.2)
        for i in range(I2C_BUFF_SIZE):
            i2cBuff[i] = i2c.read_byte_data(I2C_ADDR, i)
        levelNow = (i2cBuff[I2C_MEAS_H] * 256) + i2cBuff[I2C_MEAS_L]
        levelAvg = (i2cBuff[I2C_AVG_H] * 256)  + i2cBuff[I2C_AVG_L]
        i2cOK = True
    except:
        logging.info(f'{timestamp()} ERROR: initLightMeter() unable to access I2C '
                     f'interface at address 0x{I2C_ADDR:02x}')

    return i2cOK, levelNow, levelAvg

def getDayOrNightLevel(i2c, currDayOrNight, twilightLevelCfg, nightLevelCfg):
    """
    Using a light sensor connected via I2C, read the current average value of
    ambient darkness and compare it to the trigger levels supplied for twilight
    and night to determine whether the current darkness level indicates that
    it is currently day, twilight, or night.
    Returns:
        i2cOK - True only if I2C interface is working
        levelNow - current darkness level reading
        levelAvg - average darkness level reading
        dayOrNightChanged - True on change to/from day/twilight or twilight/night
        newDayOrNight - 'day', 'twilight', or 'night'
    """
    i2cBuff = [0] * I2C_BUFF_SIZE
    dayOrNightChanged = False
    newDayOrNight = 'day'
    levelNow = 0
    levelAvg = 0
    i2cOK = False
    try:
        for i in range(I2C_BUFF_SIZE):
            i2cBuff[i] = i2c.read_byte_data(I2C_ADDR, i)
        levelNow = (i2cBuff[I2C_MEAS_H] * 256) + i2cBuff[I2C_MEAS_L]
        levelAvg = (i2cBuff[I2C_AVG_H] * 256)  + i2cBuff[I2C_AVG_L]
        i2cOK = True
        if levelAvg >= nightLevelCfg and not currDayOrNight == 'night':
            newDayOrNight = 'night'
            dayOrNightChanged = True
        elif (levelAvg >= twilightLevelCfg and levelAvg < nightLevelCfg
              and not currDayOrNight == 'twilight'):
            newDayOrNight = 'twilight'
            dayOrNightChanged = True
        elif levelAvg < twilightLevelCfg and not currDayOrNight == 'day':
            newDayOrNight = 'day'
            dayOrNightChanged = True
        if dayOrNightChanged:
            logging.info(f'{timestamp()} getDayOrNightLevel() light level {levelAvg} '
                         f'changed settings from {currDayOrNight} to {newDayOrNight}')
        else:
            newDayOrNight = currDayOrNight
    except:
        newDayOrNight = currDayOrNight
        logging.info(f'{timestamp()} ERROR: getDayOrNightLevel() unable to access '
                     f'I2C interface at address 0x{I2C_ADDR:02x}')

    return i2cOK, levelNow, levelAvg, dayOrNightChanged, newDayOrNight

def getDayOrNight(coords, oldDayOrNight, twilightTime):
    """
    Using a Sun object from the Sun module, determine from the given coordindates and
    the current time whether it is after sunset and before sunrise.  Add twilightTime
    hours to sunrise or subtract twilightTime hours from sunset to extend the period
    considered to be nighttime.
    Returns:
        dayOrNightChanged - True on change from day to night or night to day
        newDayOrNight - 'day' or 'night'
    """
    sun = Sun.Sun()
    sunriseD = sun.getSunriseTime(coords)
    sunsetD  = sun.getSunsetTime(coords)
    ts = time.time()
    currHour = int(datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime('%H'))
    currMin = int(datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime('%M'))
    currDec = currHour + currMin / 60
    sunriseDec = sunriseD['decimal']
    sunsetDec = sunsetD['decimal']
    newDayOrNight = 'day'
    dayOrNightChanged = False
    if sunsetDec >= 12:
        if currDec > sunsetDec - twilightTime:
            newDayOrNight = 'night'
        elif currDec < sunriseDec + twilightTime:
            newDayOrNight = 'night'
    elif currDec > sunsetDec - twilightTime and currDec < sunriseDec + twilightTime:
        newDayOrNight = 'night'
    if not newDayOrNight == oldDayOrNight:
        dayOrNightChanged = True

    return dayOrNightChanged, newDayOrNight

def getLPRLogFilePath(loggingDir):
    """
    Returns a log file path in the provided directory based on the current date
    (format LPRCamYYYYMMDD.log).
    """
    dateStr = time.strftime('%Y%m%d')
    logFileName = f'LPRCam{dateStr}.log'
    logFilePath = path.join(loggingDir, logFileName)

    return logFilePath

def checkLogSwap(loggingDir, logsToKeep):
    """
    Replace the current log file with a new one if the current date no longer
    matches the active log file name.
    """
    newLogPath = getLPRLogFilePath(loggingDir)
    if not path.exists(newLogPath):
        log = logging.getLogger()
        for handler in log.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                log.removeHandler(handler)
        log.addHandler(logging.FileHandler(newLogPath, mode='a'))
        logging.basicConfig(format='%(message)s', level=logging.INFO)
    if not path.exists(newLogPath):
        print('{timestamp()}: ERROR: Failed to create new log file {newLogPath}.  Quitting.')
        _exit(1)

    # Delete the oldest log files beyond the configured number of logs to keep.
    if not logsToKeep == 0:
        pathIter = Path(loggingDir)
        logFiles = [str(file) for file in pathIter.glob('LPRCam*.log')]
        logsByAge = sorted(logFiles)
        logFileCount = len(logsByAge)
        if logFileCount > 1 and logFileCount > logsToKeep:
            logsToDelete = logFileCount - logsToKeep
            for logPath in logsByAge[0:logsToDelete]:
                proc = subprocess.run(['rm', '-f', logPath])
                logging.info(f'{timestamp()} Removed old log file {logPath}.')


#########################################################################################
# MAIN PROGRAM
#
if __name__ == '__main__':

    loggingDir       = path.join(installDir, 'log')
    captureImageDir  = path.join(installDir, 'capt_images')
    diagImageDir     = path.join(installDir, 'diag_images')
    failedImageDir   = path.join(installDir, 'failed_images')
    exitFlagDir      = installDir
    logMotFileName   = 'motion.log'
    configLPRFile    = path.join(installDir, 'LPRCam.conf')
    motionLogFile    = path.join(loggingDir, logMotFileName)

    # Set up logging.
    if not path.exists(loggingDir):
        subprocess.run(['mkdir', loggingDir])
    logLPRFilePath = getLPRLogFilePath(loggingDir)
    logHandlers = logging.StreamHandler(sys.stdout), logging.FileHandler(logLPRFilePath, mode='a')
    logging.basicConfig(format='%(message)s', level=logging.INFO, handlers=logHandlers)

    # Quit immediately if there is insufficient disk space.
    pctDiskUsed = getDiskPctUsed()
    if pctDiskUsed > MAX_PCT_DISK_USED:
        logging.info(f'{timestamp()} WARNING: Disk percent used is {pctDiskUsed}% '
                     f'(over {MAX_PCT_DISK_USED} limit).  Quitting.')
        _exit(1)

    # Make sure all required configuration and directories are present.
    if not path.exists(motionImageDir):
        logging.info(f'{timestamp()} ERROR: Cannot find input image directory \'{motionImageDir}\'.'
                     f'  Quitting.')
        _exit(1)
    if not path.exists(dayMotionCfgFilePath):
        logging.info(f'{timestamp()} ERROR: Cannot find config file \'{dayMotionCfgFilePath}\'.'
                     f'  Quitting.')
        _exit(1)
    if not path.exists(nightMotionCfgFilePath):
        logging.info(f'{timestamp()} ERROR: Cannot find config file \'{nightMotionCfgFilePath}\'.'
                     f'  Quitting.')
        _exit(1)
    if not path.exists(captureImageDir):
        subprocess.run(['mkdir', captureImageDir])
    if not path.exists(failedImageDir):
        subprocess.run(['mkdir', failedImageDir])

    # 'AUTO' - automatically turn illumination off or on during daytime or twilight/nighttime
    # 'OFF'  - illumination is always off
    # 'ON'   - illumination is always on
    illuminationCfg = 'AUTO'    # default

    # Ambient darkness level that will trigger transition from daytime configuration to
    # twilight configuration (or vice versa).  Larger values mean less light.
    twilightLevelCfg = 60

    # Ambient darkness level that will trigger transition from twiligt configuration to
    # night configuration (or vice versa).  Larger values mean less light.
    nightLevelCfg = 120

    # 'DAY'   - motion detected during daytime only
    # 'NIGHT' - motion detected during twilight or nighttime only
    # 'OFF'   - motion detection always off
    # 'ON'    - motion detection always on
    motionWhenCfg = 'ON'    # default

    # 'DAY'   - always use motion_day.conf file
    # 'NIGHT' - always use motion_night.conf file
    # 'TWILIGHT' - always use motion_twilight.conf file
    # 'AUTO'  - automatically select config file depending on ambient darkness level
    motionCfgFileSelect = 'AUTO'

    # Number of days to keep motion images before deleting them.
    keepImageDaysCfg = 3

    # Number of log files to keep (oldest ones are removed).  If set to 0, keep
    # all logs.
    logsToKeepCfg = 5

    # Number of seconds between status reports in log file.
    statusPeriodSecsCfg = 600

    # Load the configuration from the LPR config file.  If the file does not exist or if
    # loading is unsuccessful, use defaults above.
    if path.exists(configLPRFile):
        try:
            with open(configLPRFile, 'r') as configFileH:
                configDict = json.load(configFileH)
                if 'illumination' in configDict.keys():
                    illuminationCfg = configDict['illumination']
                if 'twilightLevel' in configDict.keys():
                    twilightLevelCfg = configDict['twilightLevel']
                if 'nightLevel' in configDict.keys():
                    nightLevelCfg = configDict['nightLevel']
                if 'motionWhen' in configDict.keys():
                    motionWhenCfg = configDict['motionWhen']
                if 'motionCfgSelect' in configDict.keys():
                    motionCfgFileSelect = configDict['motionCfgSelect']
                if 'keepImageDays' in configDict.keys():
                    keepImageDaysCfg = configDict['keepImageDays']
                if 'logsToKeep' in configDict.keys():
                    logsToKeepCfg = configDict['logsToKeep']
                if 'statusPeriodSecs' in configDict.keys():
                    statusPeriodSecsCfg = configDict['statusPeriodSecs']
        except:
            logging.info(f'{timestamp()} ERROR: Exception loading {configLPRFile}.  Using defaults.')

    # Configure GPIO outputs.
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(PIN_RUNNING, GPIO.OUT)
    GPIO.setup(PIN_PROCESSING, GPIO.OUT)
    GPIO.setup(PIN_IR_LED_ON, GPIO.OUT)
    GPIO.setup(PIN_IR_CUT_OFF, GPIO.OUT)
    GPIO.output(PIN_RUNNING, 0)
    GPIO.output(PIN_PROCESSING, 0)
    GPIO.output(PIN_IR_LED_ON, 0)
    GPIO.output(PIN_IR_CUT_OFF, 1)

    # Create and test I2C interface for light meter.
    i2c = smbus.SMBus(1)
    time.sleep(1.0)
    (i2cOK, levelNow, levelAvg) = initLightMeter(i2c)
    if not i2cOK:
        _exit(1)

    # If IR LED array configuration is 'ON' or 'OFF' (not 'AUTO'), apply the IR
    # LED array and IR-cut filter settings now.  'AUTO' will be handled in the
    # main loop.
    illumination = 'OFF'
    if illuminationCfg == 'ON':
        GPIO.output(PIN_IR_LED_ON, 1)
        GPIO.output(PIN_IR_CUT_OFF, 0)
        illumination = 'ON'
        logging.info(f'{timestamp()} IR LED array is now always ON.')
    elif illuminationCfg == 'OFF':
        GPIO.output(PIN_IR_LED_ON, 0)
        GPIO.output(PIN_IR_CUT_OFF, 1)
        illumination = 'OFF'
        logging.info(f'{timestamp()} IR LED array is now always OFF.')

    # If motion configuration file selection is 'DAY', 'TWILIGHT', or 'NIGHT' (not
    # 'AUTO'), apply the configuration file selection now.  'AUTO' will be handled
    # in the main loop.
    motionCfgFilePath = dayMotionCfgFilePath
    if motionCfgFileSelect == 'DAY':
        motionCfgFilePath = dayMotionCfgFilePath
    elif motionCfgFileSelect == 'TWILIGHT':
        motionCfgFilePath = twilightMotionCfgFilePath
    elif motionCfgFileSelect == 'NIGHT':
        motionCfgFilePath = nightMotionCfgFilePath

    # Main loop: scan Motion output directory for images to process and stage them
    # for processing.  Each pass also checks whether to do one of the following:
    #   1. enable or disable motion capture
    #   2. turn the IR LED array on or off
    #   3. launch motion with a new configuration
    #   4. report status
    #   5. swap the old log file with a new one if the date has changed
    #   6. exit the application (if signaled by file exitFlag)
    logging.info(f'{timestamp()} Starting main loop...')
    statusOK = True
    motionRunning = False
    motionProc = None
    motionLogFileH = None
    dayOrNightNow = 'day'
    tempHighest = 0.0
    while statusOK == True:

        try:

            # Flash the running LED to indicate program is in main loop.
            GPIO.output(PIN_RUNNING, 1)
            time.sleep(0.3)
            GPIO.output(PIN_RUNNING, 0)
            time.sleep(0.3)

            # Select configuration file based on whether it is day, twilight, or night.
            # If the light meter (via I2C interface) is available, use the light level
            # to determine day, twilight, or night.  Otherwise, use the time of day.
            # If based on time of day, extend day by 0.2 hours of twilight.
            if i2cOK:
                (i2cOK, levelNow, levelAvg, dayOrNightChanged, dayOrNightNow) = (
                    getDayOrNightLevel(i2c, dayOrNightNow, twilightLevelCfg, nightLevelCfg) )
            if not i2cOK:
                (dayOrNightChanged, dayOrNightNow) = getDayOrNight(coords, dayOrNightNow, 0.2)
            if dayOrNightNow == 'night' and motionCfgFileSelect == 'AUTO':
                motionCfgFilePath = nightMotionCfgFilePath
            elif dayOrNightNow == 'twilight' and motionCfgFileSelect == 'AUTO':
                motionCfgFilePath = twilightMotionCfgFilePath
            elif dayOrNightNow == 'day' and motionCfgFileSelect == 'AUTO':
                motionCfgFilePath = dayMotionCfgFilePath

            # Determine the IR LED array and IR-cut filter settings and apply them if
            # not already applied.
            if dayOrNightNow == 'night' or dayOrNightNow == 'twilight':
                if illuminationCfg == 'AUTO' and illumination == 'OFF':
                    GPIO.output(PIN_IR_LED_ON, 1)
                    GPIO.output(PIN_IR_CUT_OFF, 0)
                    illumination = 'ON'
                    logging.info(f'{timestamp()} IR LED array is now ON.')
            elif dayOrNightNow == 'day':
                if illuminationCfg == 'AUTO' and illumination == 'ON':
                    GPIO.output(PIN_IR_LED_ON, 0)
                    GPIO.output(PIN_IR_CUT_OFF, 1)
                    illumination = 'OFF'
                    logging.info(f'{timestamp()} IR LED array is now OFF.')

            # Determine if motion capture should be enabled or disabled.
            motionDisabled = False
            motionOnStr = 'ON'
            if motionWhenCfg == 'NIGHT' and dayOrNightNow == 'day':
                motionDisabled = True
                motionOnStr = 'OFF (for day)'
            elif motionWhenCfg == 'DAY' and (dayOrNightNow == 'night' or dayOrNightNow == 'twilight'):
                motionDisabled = True
                motionOnStr = 'OFF (for night or twilight)'
            elif motionWhenCfg == 'OFF':
                motionDisabled = True
                motionOnStr = 'OFF (always)'
            elif motionWhenCfg == 'ON':
                motionDisabled = False
                motionOnStr = 'ON (always)'

            # If the motion application is running and a configuration change is needed
            # at sunset or sunrise (or based on changes in light level), terminate the
            # current motion application process.
            if motionRunning == True and dayOrNightChanged == True:
                logging.info(f'{timestamp()} Stop motion application to apply new config.')
                motionProc.terminate()
                for attempt in range(5):
                    time.sleep(4)
                    if motionProc.poll() != None:
                        logging.info(f'{timestamp()} Terminated motion application.')
                        motionRunning = False
                        break
                    else:
                        logging.info(f'{timestamp()} ERROR: Unable to terminate motion application.')

            # Start (or restart) the motion application if it is not running and motion is enabled.
            if motionDisabled == False and motionRunning == False:
                logging.info(f'{timestamp()} Starting motion app with {motionCfgFilePath}...')
                try:
                    motionLogFileH = open(motionLogFile, 'w')
                except:
                    logging.info(f'{timestamp()} ERROR: unable to open motion log file.')
                    statusOK = False
                else:
                    motionProc = subprocess.Popen(['motion', '-c', motionCfgFilePath],
                                                  stderr=motionLogFileH)
                    returnCode = motionProc.poll()
                    if returnCode != None:
                        logging.info(f'{timestamp()} ERROR: unable to start motion application,'
                                     f'returncode={returnCode}.')
                        statusOK = False
                    else:
                        logging.info(f'{timestamp()} Started motion application.')
                        motionRunning = True

            # Terminate the current motion application process if it is running and it has
            # been disabled.
            elif motionDisabled == True and motionRunning == True:
                logging.info(f'{timestamp()} Motion capture disabled.  Stopping motion application.')
                motionProc.terminate()
                for attempt in range(5):
                    time.sleep(4)
                    if motionProc.poll() != None:
                        logging.info(f'{timestamp()} Terminated motion application.')
                        motionRunning = False
                        break
                else:
                    logging.info(f'{timestamp()} ERROR: Unable to terminate motion application.')

            # Stage the image motion files (if any) for LPR processing by moving them to the
            # captured images directory (a separate application will do the LPR processing).
            # If motion image files were found and moved, flash the processing LED.
            imagesMoved = stageMotionImages(motionImageDir, captureImageDir, diagImageDir,
                                            dayOrNightNow, levelAvg)
            if imagesMoved > 0:
                GPIO.output(PIN_PROCESSING, 1)
                time.sleep(0.3)
                GPIO.output(PIN_PROCESSING, 0)
                time.sleep(0.3)

            # Log current status if it is time for a status report.  Also purge the
            # oldest saved image files that are older than the maximum age.
            if isTimeForStatus(statusPeriodSecsCfg):
                (oldestImageAge, numImageFiles) = purgeOldFiles(captureImageDir, keepImageDaysCfg)
                (tempCPUStr, tempCPU) = getCPUTemp()
                if tempCPU > tempHighest:
                    tempHighest = tempCPU
                runningTimeSecs = time.time() - startTime
                pctDiskUsed = getDiskPctUsed()
                (i2cOK, levelNow, levelAvg, dayOrNightChanged, dayOrNightNow) = (
                    getDayOrNightLevel(i2c, dayOrNightNow, twilightLevelCfg, nightLevelCfg) )
                runningTimeStr = str(timedelta(seconds=runningTimeSecs)).split('.')[0]
                logging.info(f'{timestamp()} Status report:')
                logging.info(f'  {numImageFiles} saved image files'
                             f' (oldest: {oldestImageAge:.3f} days old)')
                logging.info(f'  settings for {dayOrNightNow}')
                logging.info(f'  motion capture {motionOnStr}')
                if i2cOK:
                    logging.info(f'  light level: current {levelNow}, average {levelAvg}')
                else:
                    logging.info(f'  light level: unknown (no I2C interface)')
                logging.info(f'  IR illumination {illumination}')
                logging.info(f'  {tempCPUStr} degrees C current CPU temperature')
                logging.info(f'  {tempHighest} degrees C highest recorded CPU temperature')
                logging.info(f'  {runningTimeStr} time running since start')
                logging.info(f'  {pctDiskUsed}% disk space used')

            # If the exit flag file is present, delete it and gracefully exit the main
            # program loop.
            exitFlagPath = path.join(exitFlagDir, 'exitFlag')
            if path.exists(exitFlagPath):
                logging.info(f'{timestamp()} Exit flag file found.  Quitting.')
                subprocess.run(['rm', '-f', exitFlagPath])
                break

            # If the system is low on disk space, exit gracefully.
            if pctDiskUsed > MAX_PCT_DISK_USED:
                logging.info(f'{timestamp()} WARNING: Disk percent used over {MAX_PCT_DISK_USED}%.'
                             f'  Quitting.')
                break

            # If the CPU temperature is too high, exit gracefully.
            if tempCPU > 85.0:
                logging.info(f'{timestamp()} WARNING: CPU temperature is {tempCPUStr}.  Quitting.')
                break

            # If the date has changed, swap out the old log file with a new one and
            # possibly purge old logs.
            checkLogSwap(loggingDir, logsToKeepCfg)

        except SystemExit:
            logging.info(f'{timestamp()} Received SystemExit.  Quitting.')
            break

        except KeyboardInterrupt:
            logging.info(f'{timestamp()} Received KeyboardInterrupt.  Quitting.')
            break

    # end of main loop

    # Perform resource cleanup before quitting.
    logging.info(f'{timestamp()} Performing cleanup...')
    if motionRunning == True and motionProc != None:
        logging.info(f'{timestamp()} Stopping motion application...')
        motionProc.terminate()
        for attempt in range(5):
            time.sleep(4)
            if motionProc.poll() != None:
                logging.info(f'{timestamp()} Terminated motion application.')
                motionRunning = False
                break
        else:
            logging.info(f'{timestamp()} ERROR: Unable to terminate motion application.')
    if motionLogFileH != None:
        motionLogFileH.close()
    GPIO.cleanup()
    logging.info(f'{timestamp()} Program exit.')
