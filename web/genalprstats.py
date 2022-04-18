#!/bin/usr/python3

# genalprstats.py:
# Generate statistics on the performance of the openalpr application, including
# the accuracy of the openalpr OCR using the minimum edit sequence that can be
# performed on an OCR result to convert it to the actual value.  The target
# directory should contain JSON files output by openalpr against images with
# license plates, but with each file modified such that the plate preceding
# the candidate list has been changed to the plate number as a result of
# manual inspection of the image.  The result of the OCR analysis may
# optionally be saved as an EditsStats object in a pickle file for use by
# other applications that know how to use EditStats.

import sys, json, pickle
from os import path, listdir, _exit
import levenshtein

def resultStats(resultFilePath):
    """
    For the given alpr JSON results file, determine if there is at least
    one plate detected.  If so, calculate the average relative x position
    of the plate.
    """
    hasPlate = False
    xRelativePos = 0
    try:
        with open(resultFilePath) as resultFileH:
            resultsDict = json.load(resultFileH)
            if len(resultsDict['results']) > 0:
                hasPlate = True
                xSum = 0
                numCoords = 0
                for coord in resultsDict['results'][0]['coordinates']:
                    xSum += coord['x']
                    numCoords += 1
                imgWidth = resultsDict['img_width']
                if numCoords > 0:
                    xRelativePos = (xSum / numCoords) / imgWidth
    except:
        print(f'ERROR: Exception accessing {resultFilePath}.')

    return hasPlate, xRelativePos

def getActualAndOCR(analFilePath, numRequested):
    """
    For the given file containing openalpr results, return the actual plate
    number and the first numRequested OCR results and their confidence values.
    """
    ocrList = [''] * numRequested
    confList = [0.0] * numRequested
    actual = ''
    imgWidth = 0
    try:
        with open(analFilePath) as analFileH:
            resultsDict = json.load(analFileH)
            if len(resultsDict['results']) == 0:
                print(f'ERROR: {analFilePath} has 0 results.')
            else:
                if not 'plate' in resultsDict['results'][0]:
                    print(f'ERROR: {analFilePath} has no plate field.')
                else:
                    imgWidth = resultsDict['img_width']
                    actual = resultsDict['results'][0]['plate']
                    if not 'candidates' in resultsDict['results'][0]:
                        print(f'ERROR: {analFilePath} has no candidates field.')
                    else:
                        numCandidates = len(resultsDict['results'][0]['candidates'])
                        if numCandidates == 0:
                            print(f'ERROR: {analFilePath} has 0 candidates.')
                        else:
                            for i in range(min(numRequested, numCandidates)):
                                ocrList[i] = resultsDict['results'][0]['candidates'][i]['plate']
                                confList[i] = resultsDict['results'][0]['candidates'][i]['confidence']
    except:
        print(f'ERROR: Exception accessing {analFilePath}.')

    return actual, imgWidth, ocrList, confList

def printUsage(program):
    print(f'Usage:\npython3 {program} results-dir analysis-dir {{output-file}}')
    print('  where results-dir is the directory containing all alpr JSON results files')
    print('  and analysis-dir is the directory containing the analyzed alpr JSON files')
    print('  and output-file is an optional pickle file containing a levenshtein.EditStats object')


######################################################################################
# Main

sys.stderr = sys.stdout
if len(sys.argv) == 1:
    printUsage(sys.argv[0])
    _exit(1)
elif len(sys.argv) > 4:
    print(f'ERROR: Too many arguments ({len(sys.argv) - 1}).')
    printUsage(sys.argv[0])
    _exit(1)
if not path.exists(sys.argv[1]):
    print(f'ERROR: No such directory {sys.argv[1]}.')
    _exit(1)
else:
    resultsDir = sys.argv[1]
if not path.exists(sys.argv[2]):
    print(f'ERROR: No such directory {sys.argv[2]}.')
    _exit(1)
else:
    analysisDir = sys.argv[2]
if len(sys.argv) == 4:
    outputFilePath = sys.argv[3]
else:
    outputFilePath = ''

# Get a sorted list of file names from the results directory.
resultFileList = sorted(listdir(resultsDir))
resultFileList = [x for x in resultFileList if x.endswith('.json')]
resultFileCount = len(resultFileList)
if resultFileCount == 0:
    print(f'ERROR: There are no result files in {resultsDir}.')
    _exit(1)

# Get a sorted list of files from the analysis directory.
analFileList = sorted(listdir(analysisDir))
analFileList = [x for x in analFileList if x.endswith('.json')]
analFileCount = len(analFileList)
if analFileCount == 0:
    print(f'ERROR: There are no result files in {analysisDir}.')
    _exit(1)

# Determine the number of results files that have at least one license
# plate.
resultsWithPlates = 0
hasLicensePlate = False
xRelativePosSum = 0
for resultFile in resultFileList:
    resultFilePath = path.join(resultsDir, resultFile)
    hasLicensePlate, xRelativePos = resultStats(resultFilePath)
    if hasLicensePlate:
        resultsWithPlates += 1
        xRelativePosSum += xRelativePos

# From the list of analyzed JSON results files, get the actual plate number
# and the highest OCR confidence results from each, calculate the Levenshtein
# distance matrix, and use the matrix to get the shortest edit sequence to
# get from the OCR result to the actual plate number.  Generate a tally of
# each substitution by source and target characters, each insertion by
# target character, and each deletion by source character.  Optionally
# export the statistics object to a pickle file.
numResults = 6
imgCountLg = 0
imgCountSm = 0
analysisCount = 0
distSum = 0
confidSum = 0.0
editStats = levenshtein.EditStats()
for analFileName in analFileList:
    analFilePath = path.join(analysisDir, analFileName)
    actual, imgWidth, ocrList, confList = getActualAndOCR(analFilePath, numResults)
    if imgWidth == 1600:
        imgCountLg += 1
    elif imgWidth == 800:
        imgCountSm += 1
    #line = f'actual={actual: >9} OCR='
    for ocrResult in ocrList:

        # Build a dictionary of the total number of occurrences of each
        # source character in the OCR results.
        editStats.addSrcOccurrences(ocrResult)

        # Build a dictionary of the total number of occurrences of each
        # target character in the actual plate number.  Note that this
        # will be incremented for each comparison of the same actual
        # plate number.
        editStats.addTgtOccurrences(actual)

        # Calculate the Levenshtein distance and edit matrix between the
        # OCR result and the actual plate number.  Retrieve the shortest
        # edit sequence from the matrix and generate statistics for each
        # type of edit action.
        dist, matrix = levenshtein.distance(ocrResult, actual)
        editSeq = levenshtein.getEditSequence(ocrResult, actual, dist, matrix)
        for edit in editSeq:
            if edit.action == 'sub':
                editStats.addSubEdit(edit.s, edit.t)
            elif edit.action == 'del':
                editStats.addDelEdit(edit.s, edit.posLbl)
            elif edit.action == 'ins':
                editStats.addInsEdit(edit.t)

        distSum += dist
        analysisCount += 1
        #line = ','.join((line, f' {ocrResult}({dist})'))

    for confidValue in confList:
        confidSum += confidValue

    #print(line)

# Display all OCR statistics.
editStats.displaySubStats()
print(' ')
editStats.displayDelStats()
print(' ')
editStats.displayInsStats()
print(' ')

pctWithPlates = 100 * resultsWithPlates / resultFileCount
xRelativePosAvg = xRelativePosSum / resultsWithPlates
pctFromLgImages = 100 * imgCountLg / analFileCount
avgDist = distSum / analysisCount
avgConfid = confidSum / analysisCount
print(f'Statistics for all results:')
print(f'   {pctWithPlates:.2f}% of results files have plates detected.')
print(f'   {xRelativePosAvg:.3f} average relative X position of plate.')
print(f'Statistics for analyzed results:')
print(f'   {analysisCount} results from {analFileCount} analysis files.')
print(f'   {pctFromLgImages:.2f} percent of analyses from large images')
print(f'   Average levenshtein distance: {avgDist:.3f}')
print(f'   Average OCR confidence: {avgConfid:.3f}')

# Export statistics to pickle file.
if not outputFilePath == '':
    try:
        with open(outputFilePath, 'wb') as pickleFileH:
            pickle.dump(editStats, pickleFileH)
            print(f'Successfully exported statistics to {outputFilePath}.')
    except:
        print(f'ERROR: Exception exporting statistics to {outputFilePath}.')
