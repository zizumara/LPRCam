#!/usr/bin/python3
# LPRserver.py
# Copyright 2022, John F. Gauthier, all rights reserved

"""
This script periodically synchronizes a local images directory with a remote images directory
that is populated with a motion activated camera.  It also generates thumbnail images from
the original images.
"""

import sys, subprocess, pwd, logging, time, fnmatch, json
from os import path, listdir, remove, setgid, setuid, chdir
from pathlib import Path
from PIL import Image

THUMB_SIZE = (100,100)


class Stats:

    def __init__(self):
        self.resultsAll = 0
        self.resultsNoPlate = 0
        self.resultsSmPlate = 0
        self.resultsLgPlate = 0
        self.resultsWithPlate = 0

    def addNew(self, noPlate, smPlate, lgPlate):
        self.resultsNoPlate += noPlate
        self.resultsSmPlate += smPlate
        self.resultsLgPlate += lgPlate
        self.resultsWithPlate += smPlate + lgPlate
        self.resultsAll += noPlate + smPlate + lgPlate
        logging.info(f'{timestamp()} New results:'
                     f' {noPlate} w/o plates,'
                     f' {smPlate} w/plates from small image'
                     f' {lgPlate} w/plates from large image.')
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


def timestamp():
    """
    Return the current time formatted as yyyy-mm-dd HH:MM:SS.
    """

    return time.strftime('%Y-%b-%d %H:%M:%S')

def demoteUser(uid, gid):
    """
    Function to be used with subprocess.Popen() as preexec_fn argument.  This allows the
    subprocess to run as a different user having the given UID and GID.
    """
    setgid(gid)
    setuid(uid)

def syncImageFiles(localUser, src, dest):
    """
    Synchronize the files in the src directory with the files in the dest directory using
    rsync.  Delete any files in the dest directory that are not in the src directory.
    """

    pwRecord = pwd.getpwnam(localUser)
    localUserUID = pwRecord.pw_uid
    localUserGID = pwRecord.pw_gid
    syncCmd = ['rsync', '-zr', '--bwlimit=400', '--delete', src, dest]
    logging.info(f'{timestamp()} Syncing image files...')
    proc = subprocess.Popen(syncCmd, preexec_fn=demoteUser(localUserUID, localUserGID))
    result = proc.wait()

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

def updateResults(imageDir, resultDir, tempDir, alprCfgDir, stats):
    """
    Given a directory containing image files and a directory containing JSON files
    of alpr results, run alpr on the images that do not already have result files.
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
    emptyResultsCreated = 0
    origResultsCreated = 0
    resizeResultsCreated = 0
    for imageFilePath in sorted(imagePathList):
        if path.exists('./exitFlag'):
            break
        imageFilename = path.basename(imageFilePath)
        resultFilename = imageFilename.replace('.jpg', '.json')
        resultFilePath = path.join(resultDir, resultFilename)
        if not path.exists(resultFilePath):
            configFile = f'{alprCfgDir}/openalpr.defaults.800x480'
            cmd = ['alpr', '-c us', f'--config {configFile}', '-j', imageFilePath]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0 and proc.returncode != 1:
                logging.info(f'{timestamp()} '
                             f'ERROR: alpr returned error code {proc.returncode}.')
            else:
                responseText = proc.stdout
                responseDict = json.loads(responseText)
                if len(responseDict['results']) > 0:
                    origResultsCreated += 1
                else:
                    try:
                        tempImage = Image.open(imageFilePath)
                        (newWidth, newHeight) = (tempImage.width * 2, tempImage.height * 2)
                        resizedImage = tempImage.resize((newWidth, newHeight), resample=Image.LANCZOS)
                        resizedImagePath = path.join(tempDir, 'resizedImage.jpg')
                        resizedImage.save(resizedImagePath ,'JPEG')
                        configFile = f'{alprCfgDir}/openalpr.defaults.1600x960'
                        cmd = ['alpr', '-c us', f'--config {configFile}', '-j', resizedImagePath]
                        proc = subprocess.run(cmd, capture_output=True, text=True)
                        if proc.returncode != 0 and proc.returncode != 1:
                            logging.info(f'{timestamp()}'
                                         f'ERROR: alpr returned error code {proc.returncode} for resized image.')
                        else:
                            responseText = proc.stdout
                            responseDict = json.loads(responseText)
                            if len(responseDict['results']) > 0:
                                resizeResultsCreated += 1
                            else:
                                emptyResultsCreated += 1
                    except:
                        logging.info(f'{timestamp()} ERROR: exception processing resized image.')
                resultFileH = open(resultFilePath, 'w')
                resultFileH.write(responseText)
                resultFileH.close()
                #resultSummary = summarizeResult(responseDict)
                #logging.info(f'{timestamp()} {imageFilename} result: {resultSummary}')
    stats.addNew(emptyResultsCreated, origResultsCreated, resizeResultsCreated)

#########################################################################################
# MAIN

localUser    = 'pizzle'
remoteUser   = 'pi'
remoteIP     = '192.168.1.68'
remoteDir    = f'/home/{remoteUser}/projects/LPRCam/capt_images/'
src          = f'{remoteUser}@{remoteIP}:{remoteDir}'
dest         = f'/home/{localUser}/web/images/'
alprCfgDir   = f'/home/{localUser}/web/openalpr-config/'
imageDir     = './images'
thumbnailDir = './thumbnails'
resultDir    = './results'
tempDir      = './temp'
updInterval  = 300.0

chdir(f'/home/{localUser}/web')
logHandlers = (logging.StreamHandler(sys.stdout), logging.FileHandler('./LPRserver.log', mode='w'))
logging.basicConfig(format='%(message)s', level=logging.INFO, handlers=logHandlers)
logging.info(f'{timestamp()} Running LPRserver.py CGI script...')
stats = Stats()

while True:
    syncImageFiles(localUser, src, dest)
    imageCount = updateThumbnails(imageDir, thumbnailDir)
    logging.info(f'{timestamp()} {imageCount} images found.')
    updateResults(imageDir, resultDir, tempDir, alprCfgDir, stats)

    # If the exit flag file is found, remove the flag file and perform a graceful exit.
    if path.exists('./exitFlag'):
        logging.info(f'{timestamp()} Exit flag file found.  Quitting.')
        remove('./exitFlag')
        break

    time.sleep(updInterval)

logging.info(f'{timestamp()} Processing finished.  Exiting.')

