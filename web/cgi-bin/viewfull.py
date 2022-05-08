#!/usr/bin/python3

"""
CGI script to view a full image from a street security camera.
"""

import sys, logging, time, json
from os import path, listdir
from PIL import Image, ExifTags
import cgi

def timestamp():
    return time.strftime('%Y-%b-%d %H:%M:%S')

def fnameToDateTime(fname):
    """
    Convert a file base name from format 'yyyymmddHHMMSS-0n' to date and time tuple
    formatted as 'yyyy-mm-dd' and 'HH:MM:SS n'.
    """
    yr = fname[0:4]
    mo = fname[4:6]
    day = fname[6:8]
    hr = fname[8:10]
    min = fname[10:12]
    sec = fname[12:14]
    num = fname[15:17]
    fdate = f'{yr}-{mo}-{day}'
    ftime = f'{hr}:{min}:{sec} {num}'
    return (fdate, ftime)

def updateVerifiedPlate(imgFileName, plateInput):
    """
    For the given image file, determine if it has a corresponding analysis file
    previously created with a plate input.  If it does, then replace the plate
    number with the new input provided.  If there is no analysis file previously
    created, the plate input is non-blank, and there is a results file with at
    least one plate result, copy the result file content, replace the result
    plate with the new plate input, and write the result to a new analysis file.
    """
    plateOutput = ''
    canUpdate = False
    if imgFileName != '':
        resultFileName = imgFileName.replace('.jpg', '.json')
        rPath = path.join('./results', resultFileName)
        analFileName = imgFileName.replace('.jpg', '.json')
        aPath = path.join('./analyzed', analFileName)
        if path.exists(aPath):
            canUpdate = True

            # An analysis file already exists.  Get its "plate" field to return
            # to the caller.  If a plate number has been provided as an input,
            # replace the "plate" field in the file.
            try:
                resultsDict = {}
                with open(aPath, 'r') as analFileH:
                    #logging.info(f'{timestamp()} Opened {aPath} for updating.')
                    try:
                        resultsDict = json.load(analFileH)
                    except:
                        logging.info(f'json.load exception: {sys.exc_info()[1]}')
                    #logging.info(f'{timestamp()} Loaded JSON from {aPath}.')
                    if len(resultsDict['results']) > 0:
                        plateOutput = resultsDict['results'][0]['plate']
                        #logging.info(f'{timestamp()} Got plate {plateOutput} from analysis file.')
                        resultsDict['results'][0]['plate'] = plateInput
                if resultsDict and plateInput != '':
                    try:
                        with open(aPath, 'w') as analFileH:
                            json.dump(resultsDict, analFileH)
                            plateOutput = plateInput
                            logging.info(f'{timestamp()} Updated analysis file {aPath} '
                                         f'with plate number {plateInput}.')
                    except:
                        logging.info(f'{timestamp()} ERROR: exception updating {aPath}.')
            except:
                logging.info(f'{timestamp()} ERROR: exception accessing {aPath}.')

        elif path.exists(rPath):

            # No analysis file exists, so if a plate number has been entered, find
            # the corresponding results file, replace its "plate" field with the one
            # provided, and write the result to a new analysis file.
            try:
                with open(rPath, 'r') as resultFileH:
                    #logging.info(f'{timestamp()} Opened {rPath} for copying.')
                    resultsDict = json.load(resultFileH)
                    #logging.info(f'{timestamp()} Loaded JSON from {rPath}.')
                    if len(resultsDict['results']) > 0:
                        canUpdate = True
                        if plateInput != '':
                            resultsDict['results'][0]['plate'] = plateInput
                            plateOutput = plateInput
                            try:
                                with open(aPath, 'w') as analFileH:
                                    #logging.info(f'{timestamp()} Opened new {aPath} for writing.')
                                    json.dump(resultsDict, analFileH)
                                    #logging.info(f'{timestamp()} Dumped JSON to {aPath}.')
                                    logging.info(f'{timestamp()} Created analysis file {aPath} '
                                                 f'with plate number {plateInput}.')
                            except:
                                logging.info(f'{timestamp()} ERROR: exception writing {aPath}.')
            except:
                logging.info(f'{timestamp()} ERROR: exception accessing {rPath}.')

    return (plateOutput, canUpdate)

def getAdjacentImages(filename):
    """
    Given a the file name of an image file, locate its position in a sorted
    list of all image files and return a tuple of file names of the previous
    current, and next images.  If the file does not exist, then the current
    file name returned is the first in the list.  The previous or next
    image file names returned may be empty strings if the current file is
    the first or last in the list.
    """
    prevFilename = ''
    currFilename = filename
    nextFilename = ''
    imageFilenames = sorted(listdir('./images'))
    if len(imageFilenames) > 0:
        if not currFilename == '':
            currPath = path.join('./images', currFilename)
            if not path.exists(currPath):
                # Current doesn't exist.  Set new current to first in list and
                # next to current + 1 if possible.  Leave prev empty.
                currFilename = imageFilenames[0]
                if len(imageFilenames) > 1:
                    nextFilename = imageFilenames[1]
            else:
                if len(imageFilenames) == 2:
                    # Only 2 images in list.  Set either prev or next depending
                    # on which one current is.
                    if currFilename == imageFilenames[0]:
                        nextFilename = imageFilenames[1]
                    else:
                        prevFilename = imageFilenames[0]
                elif len(imageFilenames) > 2:
                    # More than 2 images in list.
                    if currFilename == imageFilenames[0]:
                        # Current is first in list: next is last and prev is empty.
                        nextFilename = imageFilenames[1]
                    elif currFilename == imageFilenames[-1]:
                        # Current is last in list: prev is first and next is empty.
                        prevFilename = imageFilenames[-2]
                    else:
                        # Current is neither first nor last in list: set both prev and next.
                        currIndex = imageFilenames.index(currFilename)
                        prevFilename = imageFilenames[currIndex - 1]
                        nextFilename = imageFilenames[currIndex + 1]

    return (prevFilename, currFilename, nextFilename)

########################################################################################
# MAIN

sys.stderr = sys.stdout
logHandlers = (logging.FileHandler('./log/viewfull.log', mode='a'),)
logging.basicConfig(format='%(message)s', level=logging.INFO, handlers=logHandlers)
#logging.info(f'{timestamp()} Running viewfull.py CGI script...')

# Get form inputs supplied from home page or from this page.
form = cgi.FieldStorage()
fileExists = False
if not 'fname' in form:
    fname = ''
    logging.info(f'{timestamp()} ERROR: no "fname" parameter in input.')
else:
    fname = form['fname'].value
    #logging.info(f'{timestamp()} Requested view of {fname}.')
    fpath = path.join('./images', fname)
    exif = 'Image metadata: '
    if not path.exists(fpath):
        logging.info(f'{timestamp()} Image file {fpath} not found.')
    else:
        fileExists = True
        try:
            tempImage = Image.open(fpath)
            exifDict = { ExifTags.TAGS[k]: v for k, v in tempImage._getexif().items() if k in ExifTags.TAGS}
            if 'ImageDescription' in exifDict:
                exif += exifDict['ImageDescription']
            else:
                logging.info(f'{timestamp()} No EXIF data found in {fname}.')
            tempImage.close()
        except:
            logging.info(f'{timestamp()} Unable to read EXIF data from {fname}.')
if not 'from' in form:
    startFrom = ''
else:
    startFrom = form['from'].value
if not 'idx' in form:
    idxStr = '0'
else:
    idxStr = form['idx'].value
if not 'plt' in form:
    plateIn = ''
else:
    plateIn = form['plt'].value.upper()
if not 'res' in form:
    resIn = ''
else:
    resIn = form['res'].value
if not 'sea' in form:
    seaIn = ''
else:
    seaIn = form['sea'].value
if not 'thr' in form:
    thrIn = ''
else:
    thrIn = form['thr'].value

# If a plate number was submitted by the user on this page, create an analysis
# file or update an existing analysis file with that number.
(plate, canUpdate) = updateVerifiedPlate(fname, plateIn)
pltDis = ''
if not canUpdate:
    pltDis = 'disabled'
##########
# TBR: Revise so that results file is not required to enter plate number.
#      May require alternate analysis file format for those images that do
#      not have openalpr results.


# Determine whether next and previous images exist to determine whether next
# or previous buttons should be disabled.
(fprev, fname, fnext) = getAdjacentImages(fname)
#logging.info(f'{timestamp()} prev={fprev} curr={fname} next={fnext}')
pDis = ''
nDis = ''
if fnext == '':
    nDis = 'disabled'
if fprev == '':
    pDis = 'disabled'

print('Content-type: text/html\n')
print('<head>')
print(f'<title>Image File {fname}</title>')
print('<style>')
print('.imgText {font-family: "Arial"; color:red; font-size: 18px; border: 0; }')
print('</style>')
print('</head>')
print('<body>')

if fileExists:
    print(f'<img src="../images/{fname}" alt=[image]>')
else:
    print(f'<span class="imgText">*** Image {fname} no longer available ***</span>')

print('<form method=GET action="viewfull.py">')
print('<table><tr>')
print(f'<td><button type="submit" name="fname" value="{fprev}" {pDis}>Prev</button></td>')
print('<td><button type="submit" name="fname" value="{fname}" formaction="home.py">Home</button></td>')
print(f'<td><button type="submit" name="fname" value="{fnext}" {nDis}>Next</button></td>')
print('</tr></table>')
print(f'<input type="hidden" id="from" name="from" value="{startFrom}">')
print(f'<input type="hidden" id="idx" name="idx" value="{idxStr}">')
if not resIn == '':
    print(f'<input type="hidden" id="res" name="res" value="{resIn}">')
if not seaIn == '':
    print(f'<input type="hidden" id="sea" name="sea" value="{seaIn}">')
if not thrIn == '':
    print(f'<input type="hidden" id="thr" name="thr" value="{thrIn}">')
print('</form>')

print('<form method=GET action="viewfull.py">')
print('<table><tr>')
print('<th align="right">Actual plate number:')
print(f'<td><input type="text" name="plt" value="{plate}" {pltDis}></td>')
print(f'<td><button type="submit" name="fname" value="{fname}" formaction="viewfull.py">'
      f'Submit</button></td>')
if not plateIn == '':
    print(f'<td>&nbsp;&nbsp;Plate number {plate} saved</td>')
print('</tr></table>')
print(f'<input type="hidden" id="from" name="from" value="{startFrom}">')
print(f'<input type="hidden" id="idx" name="idx" value="{idxStr}">')
if not resIn == '':
    print(f'<input type="hidden" id="res" name="res" value="{resIn}">')
if not seaIn == '':
    print(f'<input type="hidden" id="sea" name="sea" value="{seaIn}">')
if not thrIn == '':
    print(f'<input type="hidden" id="thr" name="thr" value="{thrIn}">')
print('</form>')
print(f'<p>{exif}')
print('</body>')

#logging.info(f'{timestamp()} CGI script finished.')
