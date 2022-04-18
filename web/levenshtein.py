#!/usr/bin/python3

# levenshtein.py:
# A module that provides tools to analyze differences between strings, based on
# the Levenshtein distance as computed by the Wagner-Fischer algorithm.  Includes
# classes to hold accumulated edit statistics with methods to import/export
# from/to a statistics file.

import sys, json, pickle
from os import path

DEBUG = False

class SubEditStat:
    """
    Statistic for edit substitutions of a source character with a target
    character.
    """

    def __init__(self):
        self.total = 0
        self.errRate = 0.0
        self.tgtDict = {}

    def addEdit(self, tgtChar, totalSrcOccurs):
        """
        Increments the number of substitutions made to a target character.
        If no substitution entry exists yet in the dictionary for this target
        character, one is created.
        """
        if tgtChar in self.tgtDict:
            self.tgtDict[tgtChar] += 1
        else:
            self.tgtDict[tgtChar] = 1
        self.total += 1
        if totalSrcOccurs == 0:
            self.errRate = 1.0
        else:
            self.errRate = self.total / totalSrcOccurs

# end class SubEditStat

class InsEditStat:
    """
    Statistic for insertions of a target character into a source string.
    """
    def __init__(self):
        self.total = 0
        self.errRate = 0.0

    def addEdit(self, totalTgtOccurs):
        """
        Increments the number of insertions made of a target character.
        """
        self.total += 1
        if totalTgtOccurs == 0:
            self.errRate = 0.0
        else:
            self.errRate = self.total / totalTgtOccurs

# end class InsEditStat

class DelEditStat:
    """
    Statistic for deletions of a character from a target string by position.
    """
    def __init__(self):
        self.total = 0
        self.posDict = {}

    def addEdit(self, posLabel):
        """
        Increments the number of deletions of a target character at the given position.
        """
        if posLabel in self.posDict:
            self.posDict[posLabel] += 1
        else:
            self.posDict[posLabel] = 1
        self.total += 1

# end class DelEditStat

class EditStats:
    """
    Contains statistics for single character edits on a source string to match
    the character sequence in a target string, including substitutions, deletions,
    and insertions.
    """
    def __init__(self):
        self.subDict = {}
        self.delDict = {}
        self.insDict = {}
        self.srcOccurDict = {}
        self.tgtOccurDict = {}

    def addSrcOccurrences(self, source):
        """
        Update the total occurrences of each character for all source strings.
        """
        for char in source:
           if char in self.srcOccurDict:
               self.srcOccurDict[char] += 1
           else:
               self.srcOccurDict[char] = 1

    def addTgtOccurrences(self, target):
        """
        Update the total occurrences of each character for all target strings.
        """
        for char in target:
            if char in self.tgtOccurDict:
                self.tgtOccurDict[char] += 1
            else:
                self.tgtOccurDict[char] = 1

    def addSubEdit(self, srcChar, tgtChar):
        """
        Add a substitution edit to the substitution dictionary and update
        total occurrences of the source character.
        """
        if not srcChar in self.subDict:
            self.subDict[srcChar] = SubEditStat()
        if srcChar in self.srcOccurDict:
            totalSrcOccurs = self.srcOccurDict[srcChar]
        else:
            totalSrcOccurs = 0
        self.subDict[srcChar].addEdit(tgtChar, totalSrcOccurs)

    def getSubEditCost(self, srcChar, tgtChar):
        """
        Calculate the cost of substituting the source character for the target
        character based on accumulated substitution statistics.  The cost is based
        on the probability that the source character gets replaced with any
        character times the probability that the replacement is this particular
        target character.  If the substitution dictionary is empty, then the cost
        defaults to 1.0.
        """
        cost = 1.0
        if srcChar in self.subDict:
            if tgtChar in self.subDict[srcChar].tgtDict:
                count = self.subDict[srcChar].tgtDict[tgtChar]
                subRate = count / self.subDict[srcChar].total
                cost = (1 - self.subDict[srcChar].errRate) * (1 - subRate)
        return cost

    def displaySubStats(self):
        print('Substutions listed by source character, number of substitutions, and '
              'error rate:')
        sortedSubs = sorted(self.subDict.items(), key=lambda x: x[1].errRate, reverse=True)
        for (srcChar, sDict) in sortedSubs:
            print(f"sub '{srcChar}':{self.subDict[srcChar].total}"
                  f"({self.subDict[srcChar].errRate:.3f}) --", end='')
            line = ''
            first = True

            # Sort based on the number of occurrences of this substituted (target) character.
            sortedTgts = sorted(self.subDict[srcChar].tgtDict.items(),
                                key=lambda x: x[1], reverse=True)
            for (tgtChar, count) in sortedTgts:
                if tgtChar in self.srcOccurDict:
                    fraction = count / self.subDict[srcChar].total
                else:
                    fraction = 0.0
                formatStat = f" '{tgtChar}':{count:}({fraction:.3f})"
                if first:
                    line = formatStat
                    first = False
                else:
                    line = ','.join((line, formatStat))
            print(line)

    def addInsEdit(self, tgtChar):
        """
        Add an insertion edit to the insertion dictionary and update total
        occurrences of the target character.
        """
        if not tgtChar in self.insDict:
            self.insDict[tgtChar] = InsEditStat()
        if tgtChar in self.tgtOccurDict:
            totalTgtOccurs = self.tgtOccurDict[tgtChar]
        else:
            totalTgtOccurs = 0
        self.insDict[tgtChar].addEdit(totalTgtOccurs)

    def getInsEditCost(self, tgtChar):
        """
        Calculate the cost of inserting the target character based on accumulated
        insertion statistics.  The cost is the probability that the target character
        is omitted from any source.  If the insertion dictionary is empty, then the
        cost defaults to 1.0.
        """
        cost = 1.0
        if tgtChar in self.insDict:
            cost = 1 - self.insDict[tgtChar].errRate
        return cost

    def displayInsStats(self):
        sortedInss = sorted(self.insDict.items(), key=lambda x: x[1].errRate, reverse=True)
        for (tgtChar, iStat) in sortedInss:
            print(f"ins '{tgtChar}' -- {iStat.total:>4d} / "
                  f"{self.tgtOccurDict[tgtChar]:>4d} ({iStat.errRate:>.3f})")


    def addDelEdit(self, srcChar, posLabel):
        """
        Add a deletion edit to the deletion dictionary by character position.
        """
        if not srcChar in self.delDict:
            self.delDict[srcChar] = DelEditStat()
        self.delDict[srcChar].addEdit(posLabel)

    def getDelEditCost(self, srcChar, posLabel):
        """
        Calculate the cost of deleting the source character based on accumulated
        deletion statistics.  The cost is the probability that the source character
        does not occur in any target times the probability that the source character
        is deleted in the target for the given position label ('first', 'last',
        or 'middle').  If the deletion dictionary is empty, then the cost defaults
        to 1.0.
        """
        cost = 1.0
        if srcChar in self.delDict:
            if posLabel in self.delDict[srcChar].posDict:
                count = self.delDict[srcChar].posDict[posLabel]
                delPosRate = count / self.delDict[srcChar].total
                if not srcChar in self.tgtOccurDict:
                    delRate = 1
                else:
                    delRate = self.tgtOccurDict[srcChar] / self.srcOccurDict[srcChar]
                cost = (1 - delRate) * (1 - delPosRate)
        return cost

    def displayDelStats(self):
        for srcChar in sorted(self.delDict):
            print(f"del '{srcChar}' --", end='')
            line = ''
            first = True
            sortedDels = sorted(self.delDict[srcChar].posDict.items(),
                                key=lambda x: x[0])
            for (posLabel, count) in sortedDels:
                formatStat = f" {posLabel}:{count}"
                if first:
                    line = formatStat
                    first = False
                else:
                    line = ','.join((line, formatStat))
            print(line)

#end class EditStats

class Edit:
    def __init__(self, action, pos, srcChar, tgtChar, posLabel=''):
        self.action = action
        self.pos = pos
        self.s = srcChar
        self.t = tgtChar
        self.posLbl = posLabel

# end class Edit


###############################################################################
# Utility Functions

def exportToFile(statsObject, filePath):
    """
    Given an EditStats object, save its contents to a pickle file specified
    by filePath.
    Returns:
        isSuccessful - True if the pickle operation was successful
    """
    isSuccessful = False
    if not statsObject == None and isInstance(statsObject, EditStats):
        try:
            with open(filePath, 'wb') as fileH:
                pickle.dump(statsObject, fileH)
                isSuccessful = True
        except:
            pass   # lets isSuccessful remain False
    return isSuccessful

def importFromFile(filePath):
    """
    Given a file path to a pickle file, load the contents as an EditStats
    object.
    Returns:
        statsObject - the EditStats object if successful; None if unsuccessful
    """
    statsObject = None
    if path.exists(filePath):
        try:
            with open(filePath, 'rb') as fileH:
                statsObject = pickle.load(fileH)
        except:
            statsObject = None
    return statsObject

def distance(source, target, editStats=None):
    """
    Using a modified Wagner-Fischer algorithm, compute and return the
    Levenshtein distance between the source string and the target string,
    which is the minimum number of 1-character edit operations on the source
    string to produce the target string.  A typical application would be to
    attempt to match the output of an OCR algorithm (the source) with a known
    string (the target).  Also return the corresponding matrix, which can be
    used to determine the edit sequence.  The dimensions of the returned 
    matrix are [len(source) + 1][len(target) + 1].
    """

    # Initialize the 2D Levenstein matrix, which has one more column than the
    # length of the source and one more row than the length of the target.
    srcDimen = len(source) + 1
    tgtDimen = len(target) + 1
    dist = [[0 for tgtIdx in range(tgtDimen)] for srcIdx in range(srcDimen)]

    # The first row of the matrix represents the cost of deleting all characters
    # of the source string to match an empty target string.
    for srcIdx in range(1, srcDimen):
        if editStats == None:
            dist[srcIdx][0] = srcIdx
        else:
            posLabel = getPositionLabel(srcIdx - 1, len(source))
            delCost = editStats.getDelEditCost(source[srcIdx - 1], posLabel)
            dist[srcIdx][0] = dist[srcIdx - 1][0] + delCost

    # The first column of the matrix represents the cost of matching an empty
    # source string to a target by inserting every character of the target.
    for tgtIdx in range(1, tgtDimen):
        if editStats == None:
            dist[0][tgtIdx] = tgtIdx
        else:
            insCost = editStats.getInsEditCost(target[tgtIdx - 1])
            dist[0][tgtIdx] = dist[0][tgtIdx - 1] + insCost

    # Generate values for the rest of the rows and columns of the matrix by
    # iteratively summing the cost of each deletion, insertion, and substitution
    # for each element.
    for tgtIdx in range(1, tgtDimen):
        for srcIdx in range(1, srcDimen):
            if source[srcIdx - 1] == target[tgtIdx - 1]:
                subCost = 0
            else:
                if editStats == None:
                    subCost = 1
                else:
                    subCost = editStats.getSubEditCost(source[srcIdx - 1], target[tgtIdx - 1])
            if editStats == None:
                delCost = 1
            else:
                posLabel = getPositionLabel(srcIdx - 1, len(source))
                delCost = editStats.getDelEditCost(source[srcIdx - 1], posLabel)
            if editStats == None:
                insCost = 1
            else:
                insCost = editStats.getInsEditCost(target[tgtIdx - 1])
            toSub = dist[srcIdx - 1][tgtIdx - 1] + subCost
            toDel = dist[srcIdx - 1][tgtIdx] + delCost
            toIns = dist[srcIdx][tgtIdx - 1] + insCost
            if DEBUG:
                print(f'\nDEBUG: sub {target[tgtIdx - 1]} for {source[srcIdx - 1]} '
                      f'cost {subCost:.4f} + {dist[srcIdx - 1][tgtIdx - 1]:.4f} = {toSub:.4f}')
                print(f'DEBUG: del {source[srcIdx - 1]}       cost {delCost:.4f} + '
                      f'{dist[srcIdx - 1][tgtIdx]:.4f} = {toDel:.4f}')
                print(f'DEBUG: ins {target[tgtIdx - 1]}       cost {insCost:.4f} + '
                      f'{dist[srcIdx][tgtIdx - 1]:.4f} = {toIns:.4f}')
            dist[srcIdx][tgtIdx] = min(toDel, toIns, toSub)  # choose lowest cost path
            if DEBUG:
                displayMatrix(dist, source, target)

    return dist[srcDimen - 1][tgtDimen - 1], dist

def getPositionLabel(index, stringLen):
    """
    Translate an index of a character string into a dictionary label ('first' for 
    index 0, 'last' for the last index, and middle for all others).
    """
    if index == 0:
        label = 'first'
    elif index == stringLen - 1:
        label = 'last'
    else:
        label = 'middle'

    return label

def displayMatrix(matrix, source, target):
    """
    Display the entire Levenshtein distance matrix with source and target as column
    and row headings.
    """
    print('          ', end='')
    for char in source:
        print(f'  {char}    ', end='')
    print(' ')
    for tgtIdx in range(0, len(target) + 1):
        if tgtIdx == 0:
            print('   ', end='')
        else:
            print(f' {target[tgtIdx - 1]} ', end='')
        for srcIdx in range(0, len(source) + 1):
            print(f'{matrix[srcIdx][tgtIdx]:>.4f} ', end='')
        print(' ')

def getEditSequence(source, target, dist, mtx):
    """
    Given a source and target string and the results of a Levenshtein distance
    computation and its corresponding matrix, determine the sequence of edits
    that produce the computed distance.
    Returns:
    editSeq - a list of Edit objects containing the action ('sub', 'ins', or 'del'),
        the string position of the action performed on the source, the character
        from the source that was substituted or deleted, and the character from
        the target that was substituted or inserted
    """
    BIGNUMBER = 1000
    m, n = len(source), len(target)
    srcEditLen = m
    editSeq = []

    while m > 0 or n > 0:
        toDel = mtx[m - 1][n] if m >= 1 else BIGNUMBER
        toIns = mtx[m][n - 1] if n >= 1 else BIGNUMBER
        toSub = mtx[m - 1][n - 1] if m >= 1 and n >= 1 else BIGNUMBER
        minValue = min(toDel, toIns, toSub)
        if minValue == toSub:
            if mtx[m - 1][n - 1] < mtx[m][n]:
                edit = Edit('sub', n-1, source[m-1], target[n-1])
                editSeq.append(edit)
            m -= 1
            n -= 1
        elif minValue == toDel:
            if n == 0:
                edit = Edit('del', n, source[m-1], '', 'first')
            elif m == srcEditLen:
                edit = Edit('del', n, source[m-1], '', 'last')
            else:
                edit = Edit('del', n, source[m-1], '', 'middle')
            editSeq.append(edit)
            m -= 1
        elif minValue == toIns:
            edit = Edit('ins', n-1, '', target[n-1])
            editSeq.append(edit)
            n -= 1

    return editSeq[::-1]


if __name__ == '__main__':

    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print(f'ERROR: {sys.argv[0]} requires at least 2 arguments (a source string and target string).')
        print(f'       A path to an existing edit statistics file may be supplied as a 3rd argument.')
    else:
        lDist, matrix = distance(sys.argv[1], sys.argv[2])
        print(f'The unmodified Levenshtein distance between {sys.argv[1]} and {sys.argv[2]} is {lDist}.')
        seq = getEditSequence(sys.argv[1], sys.argv[2], lDist, matrix)
        for edit in seq:
            print(f'{edit.action} pos={edit.pos} posLbl={edit.posLbl} s={edit.s} t={edit.t}')
        if len(sys.argv) == 4:
            editStats = importFromFile(sys.argv[3])
            if editStats == None:
                print(f'ERROR: Problem importing edit stats from {sys.argv[3]}.')
            else:
                lDist, matrix = distance(sys.argv[1], sys.argv[2], editStats)
                print(f'The modified Levenshtein distance between {sys.argv[1]} '
                      f'and {sys.argv[2]} is {lDist:.3f}.')
                seq = getEditSequence(sys.argv[1], sys.argv[2], lDist, matrix)
                for edit in seq:
                    print(f'{edit.action} pos={edit.pos} posLbl={edit.posLbl} s={edit.s} t={edit.t}')
