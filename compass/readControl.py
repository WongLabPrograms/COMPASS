#!/usr/bin/python

import sys

def getFrequencies(controlFile):
    #Create empty hash to get frequencies.
    freqs = {}
    #Open control file.
    try:
        f = open(controlFile)
    except:
        print "Couldn't find the parameter file " + controlFile + ". Exiting..."
        sys.exit()
    #Read in the control file.
    lines = f.readlines()
    f.close()

    #Loop through file to get frequencies.
    i = 0
    while i < len(lines):
        if "@Frequencies" in lines[i]:
            i += 1
            while i < len(lines) and "@" not in lines[i]:
                if "#" not in lines[i]:
                    if "=" in lines[i]:
                        frequency = lines[i].split("=")
                        #Add in error checking that frequencies are floats.
                        freqs[frequency[0]] = float(frequency[1])
                i += 1
            break
        i += 1
    lengthOfSymbols(freqs)
    return freqs

#Adds a warning if different symbols have different numbers of characters, as that's 
#almost certain to cause a crash.
def lengthOfSymbols(freqs):
    for freq in freqs:
        #Create array of keys to the hash.
        keys = []
        for key in freq:
            keys.append(key)
        #Now check they're all equal, throw warning if they aren't.
        length = len(keys[0])
        for i in range(1,len(keys)):
            newlen = len(keys[i])
            if length != newlen:
                print "WARNING: Not all symbols have the same number of characters. Program may crash unless phylip format is used."
            length = newlen

def getMultipliers(controlFile):
    #Create empty hash to get multipliers.
    multipliers = {}
    
    #Open control file.
    try:
        f = open(controlFile)
    except:
        print "Couldn't find the parameter file " + controlFile + ". Exiting..."
        sys.exit()
    #Read in the control file.
    lines = f.readlines()
    f.close()
    
    #Loop through file to get multipliers.
    i = 0

    while i < len(lines):
        if "@Multipliers" in lines[i]:
            i += 1
            while i < len(lines) and "@" not in lines[i]:
                if "#" not in lines[i]:
                    if "=" in lines[i]:
                        multi = lines[i].split("=")
                        #Add in error checking that frequencies are floats.
                        multipliers[multi[0]] = float(multi[1])
                i += 1
            break
        i += 1

    return multipliers


def getMatrix(controlFile):
    matrix = []

    #Open up the control file.
    try:
        f = open(controlFile)
    except:
        print "Couldn't find the parameter file " + controlFile + ". Exiting..."
        sys.exit()
    #Read in the control file.
    lines = f.readlines()
    f.close()

    #Loop through to get the matrix.
    i = 0
    while i < len(lines):
        if "@Matrix" in lines[i]:
            i += 1
            while i < len(lines) and "@" not in lines[i]:
                if "#" not in lines[i]:
                    line = lines[i].split()
                    if len(line) > 0:
                        matrix.append(line)
                i += 1
            break
        i += 1
        
    return matrix
