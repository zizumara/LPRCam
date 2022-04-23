#!/usr/bin/python3
# LPRserver.py
# Copyright 2022, John F. Gauthier, all rights reserved

"""
This script periodically synchronizes a local images directory with a remote images directory
that is populated with a motion activated camera.  It also generates thumbnail images from
the original images.
"""

from multiprocessing import Pool
import sys, subprocess, pwd, logging, time, datetime, fnmatch, json, shutil
from os import path, listdir, remove, setgid, setuid, chdir
from pathlib import Path
from PIL import Image

THUMB_SIZE = (100,100)
IMG_SKIPPED  = 0
IMG_NO_PLATE = 1
IMG_SM_PLATE = 2
IMG_LG_PLATE = 3

class Stats:

    def __init__(self):
        self.resultsAll = 0
        self.resultsNoPlate = 0
        self.resultsSmPlate = 0
        self.resultsLgPlate = 0
        self.resultsWithPlate = 0
        self.newResultsNoPlate = 0
        self.newResultsSmPlate = 0
        self.newResultsLgPlate = 0

    def addNew(self, noPlate=0, smPlate=0, lgPlate=0):
        self.newResultsNoPlate += noPlate
        self.newResultsSmPlate += smPlate
        self.newResultsLgPlate += lgPlate

    def report(self):
        logging.info(f'{timestamp()} New results:'
                     f' {self.newResultsNoPlate} w/o plates,'
                     f' {self.newResultsSmPlate} w/plates from small image'
                     f' {self.newResultsLgPlate} w/plates from large image.')
        self.resultsNoPlate += self.newResultsNoPlate
        self.resultsSmPlate += self.newResultsSmPlate
        self.resultsLgPlate += self.newResultsLgPlate
        self.resultsWithPlate += self.newResultsSmPlate + self.newResultsLgPlate
        self.resultsAll += self.newResultsSmPlate + self.newResultsLgPlate + self.newResultsNoPlate
        self.newResultsNoPlate = 0
        self.newResultsSmPlate = 0
        self.newResultsLgPlate = 0
        if self.resultsAll == 0:
            pctWithPlate = 0.0
        else:
            pctWithPlate = self.resultsWithPlate/self.resultsAll
        if self.resultsWithPlate == 0:
            pctSmPlate = 0.0
            pctLgPlate = 0.0
        else:
            pctSmPlate = 100 * self.resultsSmPlate/self.resultsWithPlate
            pctLgPlate = 100 * self.resultsLgPlate/self.resultsWithPlate
        logging.info(f'{timestamp()} Since start: {self.resultsAll} images,'
                     f' {pctWithPlate:.2f}% with plates,'
                     f' {pctSmPlate:.2f}% from small images,'
                     f' {pctLgPlate:.2f}% from large images.')

# End class Stats


def timestamp():
    """
    Return the current time formatted as yyyy-mmm-dd HH:MM:SS.
    """

    return time.strftime('%Y-%b-%d %H:%M:%S')

def fileTimeStr(daysInPast=None):
    """
    Return either the current time or the time some number of days in the past, formatted
    as yyyymmddHHMMSS (suitable for comparing captured image file names).
    """
    if daysInPast == None:
        return time.strftime('%Y%m%d%H%M%S')
    else:
        oldDate = datetime.datetime.now() - datetime.timedelta(daysInPast)
        return oldDate.strftime('%Y%m%d%H%M%S')

def demoteUser(uid, gid):
    """
    Function to be used with subprocess.Popen() as preexec_fn argument.  This allows the
    subprocess to run as a different user having the given UID and GID.
    """
    setgid(gid)
    setuid(uid)

def syncImageFiles(localUser, remoteDir, localDir, procDir, oldestDays):
    """
    Synchronize the files in the local directory with the files in the remote directory using
    rsync (also removes files in the local directory that are not in the remote directory).
    Next, remove files in the processing directory that are older than oldestDays.  Finally,
    copy any files that are not already in the processing directory from the local directory
    to the processing directory.
    """

    pwRecord = pwd.getpwnam(localUser)
    localUserUID = pwRecord.pw_uid
    localUserGID = pwRecord.pw_gid
    syncCmd = ['rsync', '-zr', '--bwlimit=400', '--delete', remoteDir, localDir]
    logging.info(f'{timestamp()} Syncing image files...')
    proc = subprocess.Popen(syncCmd, preexec_fn=demoteUser(localUserUID, localUserGID))
    result = proc.wait()
    oldestFilePrefix = fileTimeStr(daysInPast=oldestDays)
    syncFiles = sorted(listdir(localDir))
    procFiles = sorted(listdir(procDir))
    filesRemoved = 0
    for fileName in procFiles:
        if fileName < oldestFilePrefix:
            filePath = path.join(procDir, fileName)
            remove(filePath)
            filesRemoved += 1
    logging.info(f'{timestamp()} Removed {filesRemoved} images older than {oldestDays} days.')
    newFiles = [file for file in syncFiles if file not in procFiles]
    filesCopied = 0
    for fileName in newFiles:
        filePath = path.join(localDir, fileName)
        shutil.copy2(filePath, procDir)
        filesCopied += 1

def updateThumbnails(imageDir, thumbnailDir):
    """
    For the given image directory containing JPEG files, create corresponding thumbnail JPEG
    images in the given thumbnail directory unless they already exist.  Thumbnail images have
    the same root file name as their corresponding original images with '_thm' appended.
    Remove any existing thumbnail images for which there is no corresponding original image
    file.
    Returns: imageCount - the current number of image files that exist
    """

    # Remove any thumbnail files that don't have corresponding image files.
    thumbPathIter = Path(thumbnailDir)
    thumbsPathList = [str(file) for file in thumbPathIter.glob('*_thm.jpg')]
    thumbsRemoved = 0
    for thumbFilePath in thumbsPathList:
        if path.exists('./exitFlag'):
            break
        imageFilename = path.basename(thumbFilePath).replace('_thm.jpg', '.jpg')
        imageFilePath = path.join(imageDir, imageFilename)
        if not path.exists(imageFilePath):
            thumbsRemoved += 1
            remove(thumbFilePath)
    #logging.info(f'{timestamp()} Removed {thumbsRemoved} old thumbnail files.')

    # Create thumbnail files for image files that don't already have them.
    imagePathIter = Path(imageDir)
    imagesPathList = [str(file) for file in imagePathIter.glob('*.jpg')]
    imageCount = len(imagesPathList)
    thumbsCreated = 0
    for imageFilePath in sorted(imagesPathList):
        if path.exists('./exitFlag'):
            break
        thumbFilename = path.basename(imageFilePath).replace('.jpg', '_thm.jpg')
        thumbFilePath = path.join(thumbnailDir, thumbFilename)
        if not path.exists(thumbFilePath):
            try:
                srcImage = Image.open(imageFilePath)
            except:
                logging.info(f'{timestamp()} ERROR: Unable to open {imageFilePath} as image.')
            else:
                srcImage.thumbnail(THUMB_SIZE)
                srcImage.save(thumbFilePath)
                thumbsCreated += 1
    #logging.info(f'{timestamp()} Created {thumbsCreated} new thumbnail files.')
    return imageCount

def summarizeResult(resultDict):
    """
    Given a dictionary created from alpr analysis of an image file, generate and return
    a single text line summary of the results.
    """

    summary = 'No plate found'
    if len(resultDict['results']) > 0:
        for resultD in resultDict['results']:
            summary = ('plate %s(%4.1f), candidates: ' %
                      (resultD['plate'], resultD['confidence']))
            for candidateD in resultD['candidates']:
                candStr = ('%s(%4.1f) ' % (candidateD['plate'], candidateD['confidence']))
                summary = ''.join([summary, candStr])
    return summary

def updateResults(imageDir, resultDir, alprCfgDir, stats):
    """
    Given a directory containing image files and a directory containing JSON files
    of alpr results, run alpr on the images that do not already have result files,
    using subprocess.Pool to take advantage of multiple cores.
    Remove any old result files if their corresponding image files no longer exist.
    """

    #logging.info(f'{timestamp()} Updating license plate results...')

    # Remove any results files that don't have corresponding image files.
    resultPathIter = Path(resultDir)
    resultPathList = [str(file) for file in resultPathIter.glob('*.json')]
    resultsRemoved = 0
    for resultFilePath in resultPathList:
        imageFilename = path.basename(resultFilePath).replace('.json', '.jpg')
        imageFilePath = path.join(imageDir, imageFilename)
        if not path.exists(imageFilePath):
            resultsRemoved += 1
            remove(resultFilePath)
    #logging.info(f'{timestamp()} Removed {resultsRemoved} old license plate results files.')

    # Create results files for image files that don't already have them.
    imagePathIter = Path(imageDir)
    imagePathList = [str(file) for file in imagePathIter.glob('*.jpg')]
    imagePathList = sorted(imagePathList)
    pool = Pool()
    resultList = pool.map(processALPR, imagePathList)
    pool.close()
    for result in resultList:
        if result == IMG_NO_PLATE:
            stats.addNew(noPlate=1)
        elif result == IMG_SM_PLATE:
            stats.addNew(smPlate=1)
        elif result == IMG_LG_PLATE:
            stats.addNew(lgPlate=1)
    stats.report()

def processALPR(imageFilePath):
    """
    Run the given image through OpenALPR and generate a .JSON results file.  If no plate
    was found in the original image, resize it to twice the original size and try again.
    """

    resultStatus = IMG_SKIPPED
    if not path.exists('./exitFlag'):
        imageFilename = path.basename(imageFilePath)
        resultFilename = imageFilename.replace('.jpg', '.json')
        resultFilePath = path.join(resultDir, resultFilename)
        if not path.exists(resultFilePath):
            configFile = f'{alprCfgDir}/openalpr.defaults.800x480'
            cmd = ['alpr', '-c us', f'--config {configFile}', '-j', imageFilePath]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0 and proc.returncode != 1:
                logging.info(f'{timestamp()} ERROR: alpr returned error code {proc.returncode}.')
            else:
                responseText = proc.stdout
                responseDict = json.loads(responseText)
                if len(responseDict['results']) > 0:
                    resultStatus = IMG_SM_PLATE
                else:
                    try:
                        tempImage = Image.open(imageFilePath)
                        (newWidth, newHeight) = (tempImage.width * 2, tempImage.height * 2)
                        resizedImage = tempImage.resize((newWidth, newHeight), resample=Image.LANCZOS)
                        resizedFilePath = path.join('./temp', imageFilename)
                        resizedImage.save(resizedFilePath ,'JPEG')
                        configFile = f'{alprCfgDir}/openalpr.defaults.1600x960'
                        cmd = ['alpr', '-c us', f'--config {configFile}', '-j', resizedFilePath]
                        proc = subprocess.run(cmd, capture_output=True, text=True)
                        if proc.returncode != 0 and proc.returncode != 1:
                            logging.info(f'{timestamp()}'
                                         f'ERROR: alpr returned error code {proc.returncode} for resized image.')
                        else:
                            responseText = proc.stdout
                            responseDict = json.loads(responseText)
                            if len(responseDict['results']) > 0:
                                resultStatus = IMG_LG_PLATE
                            else:
                                resultStatus = IMG_NO_PLATE
                        remove(resizedFilePath)
                    except:
                        logging.info(f'{timestamp()} ERROR: exception processing resized image.')
                resultFileH = open(resultFilePath, 'w')
                resultFileH.write(responseText)
                resultFileH.close()
                #resultSummary = summarizeResult(responseDict)
                #logging.info(f'{timestamp()} {imageFilename} result: {resultSummary}')
    return resultStatus


#########################################################################################
# MAIN

localUser    = 'pizzle'
remoteUser   = 'pi'
remoteIP     = '192.168.1.68'
remoteDir    = f'{remoteUser}@{remoteIP}:/home/{remoteUser}/projects/LPRCam/capt_images/'
localDir     = f'/home/{localUser}/web/sync/'
alprCfgDir   = f'/home/{localUser}/web/openalpr-config/'
imageDir     = './images'
thumbnailDir = './thumbnails'
resultDir    = './results'
updInterval  = 300.0  # Delay between attempts to sync files from camera system
oldestDays   = 3.0    # Remove captured images older than this

chdir(f'/home/{localUser}/web')
logHandlers = (logging.StreamHandler(sys.stdout), logging.FileHandler('./LPRserver.log', mode='w'))
logging.basicConfig(format='%(message)s', level=logging.INFO, handlers=logHandlers)
logging.info(f'{timestamp()} Running LPRserver.py CGI script...')
stats = Stats()

while True:
    if path.exists('./exitFlag'):
        logging.info(f'{timestamp()} Exit flag file found.  Quitting.')
        remove('./exitFlag')
        break
    syncImageFiles(localUser, remoteDir, localDir, imageDir, oldestDays)
    imageCount = updateThumbnails(imageDir, thumbnailDir)
    logging.info(f'{timestamp()} {imageCount} images available.')
    updateResults(imageDir, resultDir, alprCfgDir, stats)

    # If the exit flag file is found, remove the flag file and perform a graceful exit.
    if path.exists('./exitFlag'):
        logging.info(f'{timestamp()} Exit flag file found.  Quitting.')
        remove('./exitFlag')
        break

    time.sleep(updInterval)

logging.info(f'{timestamp()} Processing finished.  Exiting.')

