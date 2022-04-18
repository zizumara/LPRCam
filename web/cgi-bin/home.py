#!/usr/bin/python3
# Copyright 2021 John F. Gauthier

"""
home.py:
CGI script for street security camera home page.
"""

import sys, logging, time, fnmatch, json, cgi, re
from datetime import datetime
from os import path, listdir, getcwd
from io import StringIO
sys.path.append(getcwd())
import levenshtein

THUMB_SIZE = (100,100)
location = 'My camera location'

class CaptureResults:

    def __init__(self, thumbFile, numRequested):
        self.thumbFile = thumbFile
        self.imageFile = thumbFile.replace('_thm.jpg', '.jpg')
        self.resultFile = thumbFile.replace('_thm.jpg', '.json')
        self.resultPath = path.join('./results', self.resultFile)
        self.analysisPath = path.join('./analyzed', self.resultFile)
        self.actualPlate = ''
        self.candPlates = []
        self.confidences = []
        self.matchCand = ''
        self.matchDist = 0.0
        if numRequested > 10:
            numRequested = 10
        if path.exists(self.resultPath):
            try:
                with open(self.resultPath) as resultFileH:
                    resultsDict = json.load(resultFileH)
                    if len(resultsDict['results']) > 0:
                        candIndex = 0
                        for resultD in resultsDict['results']:
                            for candidateD in resultD['candidates']:
                                self.candPlates.append(candidateD['plate'])
                                self.confidences.append(candidateD['confidence'])
                                candIndex += 1
                                if candIndex == numRequested:
                                    break
                            if candIndex == numRequested:
                                break
            except:
                logging.info(f'{timestamp()} ERROR: exception accessing {self.resultPath}.')

            self.actualPlate = getAnalysisResult(self.analysisPath)

    def getFormattedResults(self):
        """
        Return a list of strings representing the highest confidence openalpr result
        and its confidence value.  If there was an actual plate flagged in the results,
        then return the actual plate number as the first list item and "** verified **"
        as the second list item.  If no results file is available, return "pending" and
        "results...".  If there is a match candidate resulting from a plate search,
        include the match candidate and its Levenshtein distance as two additional
        strings.
        """
        blankResult = '&nbsp;' * 14
        resultsList = [blankResult] * 4
        if not self.actualPlate == '':
            resultsList[0] = self.actualPlate
            resultsList[1] = '** verified **'
            if not self.matchCand == '':
                resultsList[2] = f'{self.matchDist:.4f} match'
        else:
            if not path.exists(self.resultPath):
                resultsList[0] = '&nbsp;&nbsp;pending&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                resultsList[1] = '&nbsp;&nbsp;results...&nbsp;&nbsp;'
            else:
                if len(self.candPlates) > 0:
                    candPlusQ = self.candPlates[0] + '&nbsp;?'
                    plateStr = f'{candPlusQ:_<10}'
                    resultsList[0] = plateStr.replace('_', '&nbsp;')
                    resultsList[1] = f'best OCR {self.confidences[0]:>.1f}%'
                    if not self.matchCand == '':
                        matchStr = f'{self.matchCand:_<14}'
                        resultsList[2] = matchStr.replace('_', '&nbsp')
                        resultsList[3] = f'{self.matchDist:.4f} match'

        return resultsList

# end class CaptureResults

def timestamp():
    return time.strftime('%Y-%b-%d %H:%M:%S')

def dtLocalToFileRoot(dtlocal):
    """
    Convert a datetime-local HTML form input of the form yyyy-mm-ddTHH:MM to the
    root of an image file name of the form yyyymmddHHMMSS-00 for sorting and
    filtering.
    """
    yr = dtlocal[0:4]
    mo = dtlocal[5:7]
    day = dtlocal[8:10]
    hr = dtlocal[11:13]
    min = dtlocal[14:16]
    return f'{yr}{mo}{day}{hr}{min}00-00'

def fnameToFmtDateTime(fname):
    """
    Convert a file base name from format 'yyyymmddHHMMSS-0n' to date and time tuple
    formatted as 'yyyy-mm-dd' and 'HH:MM:SS n'.  The base name may include the
    optional suffix '-d|t|nLLL' indicating the capture condition day, twilight, or
    night and the darkness level LLL.  Return the lighting suffix if supplied.
    """
    fdate = 'yyyy-mm-dd'
    ftime = 'HH:MM:SS \#n'
    light = '????'
    pattern = re.compile('(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})\-0(\d)(\-([dtn]\d{3}))*')
    m = pattern.match(fname)
    if m == None:
        logging.info(f'ERROR: {fname} file name not in expected format.')
    else:
        fdate = f'{m.group(1)}-{m.group(2)}-{m.group(3)}'
        hr = int(m.group(4))
        ampm = 'AM'
        if hr >= 12:
            ampm = 'PM'
        if hr > 12:
            hr = hr - 12
        pound = '#'
        ftime = f'{hr}:{m.group(5)}:{m.group(6)} {ampm} {pound}{m.group(7)}'
        light = m.group(9)
        if light == None:
            light = ''
    return (fdate, ftime, light)

def fnameToFmtDateTimeOld(fname):
    fnameToFmtDateTimeRe(fname)
    yr = fname[0:4]
    mo = fname[4:6]
    day = fname[6:8]
    hr = fname[8:10]
    min = fname[10:12]
    sec = fname[12:14]
    num = '#' + fname[16:17]
    fdate = f'{yr}-{mo}-{day}'
    ampm = 'AM'
    if int(hr) >= 12:
        ampm = 'PM'
    if int(hr) > 12:
        hr = str(int(hr) - 12)
    ftime = f'{hr}:{min}:{sec} {ampm} {num}'
    light = ''
    return (fdate, ftime, light)

def getAnalysisResult(analFilePath):
    """
    Locate an analysis file and, if it exists, extract the plate field from the
    first result dictionary and return it.  Each analysis file is a copy of a JSON
    file produced by openalpr, but with the plate field of the first result
    replaced by a user who verified the actual plate by viewing the captured image.
    """
    analResult = ''
    if path.exists(analFilePath):
        try:
            with open(analFilePath) as analysisFileH:
                resultsDict = json.load(analysisFileH)
                if len(resultsDict['results']) > 0:
                    if 'plate' in resultsDict['results'][0]:
                        analResult = resultsDict['results'][0]['plate']
                    else:
                        logging.info(f'{timestamp()} ERROR: {analFilePath} has no plate field.')
                else:
                    logging.info(f'{timestamp()} ERROR: {analFilePath} has 0 results.')
        except:
            logging.info(f'{timestamp()} ERROR: unable to get plate from {analFilePath}.')

    return analResult


########################################################################################
# MAIN

sys.stderr = sys.stdout
logHandlers = (logging.FileHandler('./log/home.log', mode='w'),)
logging.basicConfig(format='%(message)s', level=logging.INFO, handlers=logHandlers)
logging.info(f'{timestamp()} Running home.py CGI script...')

# Check for default starting time from datetime-local form input.
form = cgi.FieldStorage()
if 'from' in form:
    initTime = form['from'].value
    fromInit = f'value="{initTime}"'
    firstThumb = dtLocalToFileRoot(initTime)
else:
    initTime = ''
    fromInit = ''
    firstThumb = ''

# Check for starting thumbnail index from form input.
index = 0
if 'idx' in form:
    indexStr = form['idx'].value
    try:
        index = int(indexStr)
    except:
        index = 0

# Check for results only flag from results only check box input.
resultsOnly = False
resOnlyStr = ''
resChk = ''
if 'res' in form:
    resOnlyStr = form['res'].value
    if resOnlyStr == 'Y':
        resultsOnly = True
        resChk = 'checked'

# Check for search plate from text box form input.
searchPlate = ''
if 'sea' in form:
    searchPlate = form['sea'].value

# Check for Levenshtein distance threshold from radio button form input.
distThresh = 4.0
thrList = [3.0, 2.6, 2.2, 1.8, 1.4, 1.0]
thrChk = [''] * len(thrList)
thrChk[0] = 'checked'   # weak threshold checked by default
thrStr = ''
if 'thr' in form:
    try:
        thrStr = form['thr'].value
        thrIndex = int(thrStr)
        thrChk = [''] * len(thrList)
        thrChk[thrIndex] = 'checked'
        distThresh = thrList[thrIndex]
    except:   # If invalid, take default
        pass

print('Content-type: text/html\n')
print('<head>')
print('<title>Street Security Home Page</title>')
print('<style>')
print('.imgText {font-family: "Courier New", monospace; font-size: 12px; border: 0; '
      'font-weight: bold; }')
print('.verText {font-family: "Courier New", monospace; font-size: 12px; border: 0; '
      'font-weight: bold; color: green; }')
print('.resText {font-family: "Courier New", monospace; font-size: 12px; border: 0; '
      'font-weight: bold; color: blue; }')
print('.warnText {font-family: "Arial"; font-size: 16px; color: red; border: 0; }')
print('.sumText {font-family: "Arial"; font-size: 14px; border: 0;}')
print('</style>')
print('</head>')
print(f'<h1>{location}</h1>')
print('<body>')

# List the current thumbnail files sorted by name (i.e. capture date and time)
# and exclude those earlier than the ones specified by the starting time from
# the form input.
numResults = 10
thumbFileList = sorted(listdir('./thumbnails'))
logging.info(f'{timestamp()} {len(thumbFileList)} thumbnail files found.')
if not firstThumb == '':
    thumbFileList = [x for x in thumbFileList if x >= firstThumb]
captureList = []
if resultsOnly and searchPlate == '':
    for resultThumbFile in thumbFileList:
        captureResults = CaptureResults(resultThumbFile, numResults)
        if len(captureResults.candPlates) > 0:
            captureList.append(captureResults)
elif not searchPlate == '':
    statsFile = 'ocrstats.pickle'
    editStats = levenshtein.importFromFile(statsFile)
    for searchThumbFile in thumbFileList:
        captureResults = CaptureResults(searchThumbFile, numResults)
        match = False
        minDist = 100.0
        captureResults.matchDist = 100.0
        for candidate in captureResults.candPlates:
            (levensDist, matrix) = levenshtein.distance(candidate, searchPlate, editStats)
            minDist = min(levensDist, minDist)
            if minDist < distThresh and minDist < captureResults.matchDist:
                match = True
                captureResults.matchCand = candidate
                captureResults.matchDist = minDist
        if match:
            captureList.append(captureResults)
else:
    for everyThumbFile in thumbFileList:
        captureList.append(CaptureResults(everyThumbFile, numResults))

lastRow = 3
lastCol = 10
tableSize = lastRow * lastCol
rowNum = 1
colNum = 1
fname1st = ''
tableEntries = 0
numCaptResults = len(captureList)

# Calculate starting image index for previous and next page controls.
if index >= numCaptResults:
    index = numCaptResults - 1
if index < 0:
    index = 0
idxStr = str(index)
nDis = ''
nextIdx = index + tableSize
if nextIdx >= numCaptResults:
    nextIdx = numCaptResults - 1
    nDis = 'disabled'
pDis = ''
prevIdx = index - tableSize
if prevIdx < 0:
    prevIdx = 0
    pDis = 'disabled'

# Prepare the image table contents.
if len(captureList) > 0:
    with StringIO() as imgTable:
        print('<table border=1>', file=imgTable)
        lastCaptIdx = len(captureList) - 1
        logging.info(f"{timestamp()} scanning captureList from {index} to {lastCaptIdx}...")
        fname1st = captureList[0].imageFile
        for i in range(index, numCaptResults):
            tableEntries += 1
            thumbFilename = captureList[i].thumbFile
            thumbPath = path.join('../thumbnails', thumbFilename)   # relative to cgi-bin
            imageFilename = captureList[i].imageFile
            (capDate, capTime, light) = fnameToFmtDateTime(thumbFilename)
            resultsList = captureList[i].getFormattedResults()
            if colNum == 1:
                print('<tr>', file=imgTable)    # start new row

            # Each cell in the main table row contains a table with a single column to
            # organize the thumbnail and its details vertically.
            print('<td><table>', file=imgTable)
            print(f'<tr><td><a href="viewfull.py?fname={imageFilename}&from={initTime}&'
                  f'idx={idxStr}&res={resOnlyStr}&sea={searchPlate}&thr={thrStr}">'
                  f'<img src="{thumbPath}" border=1 alt=[image]></a></td></tr>',
                  file=imgTable)
            print(f'<tr><td><span class="imgText">{capDate}</span></td></tr>', file=imgTable)
            print(f'<tr><td><span class="imgText">{capTime}</span></td></tr>', file=imgTable)
            for result in resultsList:
                if captureList[i].actualPlate == '':
                    print(f'<tr><td><span class="resText">{result}</span></td></tr>',
                          file=imgTable)
                else:
                    print(f'<tr><td><span class="verText">{result}</span></td></tr>',
                          file=imgTable)
            print(f'<tr><td><span class="imgText">lighting: {light}</span></td></tr>', file=imgTable)
            print(f'</table></td>', file=imgTable)

            colNum += 1
            if colNum > lastCol:
                colNum = 1
                print('</tr>', file=imgTable)    # end current row
                rowNum += 1
                if rowNum > lastRow:             # end the table
                    break

        print('</table>', file=imgTable)
        tableContent = imgTable.getvalue()

# Display search criteria and page control section at top of page.
print(f'<span class="warnText">'
      f'Captured images will remain available for 3 days after capture. '
      f'After that, they will be deleted automatically.'
      f'</span>')
#print(f'<span class="warnText">'
#      f'The camera is currently offline for maintenance, so new images will not '
#      f'be available until further notice.'
#      f'</span>')
print('<hr>')
print('<form method=GET>')
print('<label for="start">Show images starting from:</label>')
print(f'<input id="start" type="datetime-local" name="from" {fromInit}>')
print('<br>')

print('<table>')
print('<tr>')
print('<td>Search for license:</td>')
print(f'<td><input type="text" size=10 name="sea" id="sea" value="{searchPlate}"></input></td>')
print(f'<td>&nbsp;&nbsp;&nbsp;Match strength, weak ({thrList[0]}) to strong ({thrList[5]}):</td>')
print('<td>')
print(f'<input type="radio" id="thr0" name="thr" value="0" {thrChk[0]}>')
print(f'<label for="thr0">&gt;{thrList[0]}&nbsp;&nbsp;</label>')
print(f'<input type="radio" id="thr1" name="thr" value="1" {thrChk[1]}>')
print(f'<label for="thr1">{thrList[1]}&nbsp;&nbsp;</label>')
print(f'<input type="radio" id="thr2" name="thr" value="2" {thrChk[2]}>')
print(f'<label for="thr2">{thrList[2]}&nbsp;&nbsp;</label>')
print(f'<input type="radio" id="thr3" name="thr" value="3" {thrChk[3]}>')
print(f'<label for="thr3">{thrList[3]}&nbsp;&nbsp;</label>')
print(f'<input type="radio" id="thr4" name="thr" value="4" {thrChk[4]}>')
print(f'<label for="thr4">{thrList[4]}&nbsp;&nbsp;</label>')
print(f'<input type="radio" id="thr5" name="thr" value="5" {thrChk[5]}>')
print(f'<label for="thr5">&le;{thrList[5]}&nbsp;&nbsp;</label>')
print('</td>')
print('</tr>')
print('</table>')

print(f'<input type="checkbox" name="res" value="Y" id="res" {resChk}>')
print('<label for="res">Show only detected plates</label>')
print('<br><br>')
print(f'<button type="submit" name="fname" value="{fname1st}" '
      f'formaction="home.py?idx={idxStr}">Apply Filters</button>')
print('<br><hr>')

print('<table>')
print('<tr>')
print(f'<td><button type="submit" name="idx" value="{prevIdx}" '
      f'formaction="home.py" {pDis}>Prev Page</button></td>')
print(f'<td><button type="submit" name="idx" value="{nextIdx}" '
      f'formaction="home.py" {nDis}>Next Page</button></td>')
print('</tr>')
print('</table>')

print('</form>')

# Display image table section.
if tableEntries > 0:
    firstEntry = index + 1
    lastEntry = index + tableEntries
    print('<table>')
    print(f'<tr><td><span class="sumText">'
          f'Click on any image thumbnail to view it at full resolution.'
          f'</span></td></tr>')
    print(f'<tr><td><span class="sumText">'
          f'Displaying {firstEntry} - {lastEntry} of {numCaptResults} images'
          f'</span></td></tr>')
    print('</table>')
    print(tableContent)
else:
    print('<span class="warnText">*** No images match the search criteria ***</span>')

print('</body>')

logging.info(f'{timestamp()} CGI script finished.')
